from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd
from psycopg2.extras import RealDictCursor, execute_values

CACHE_PATH = "top5_cache.json"

# =============================================================================
# Flow (this module: pure scoring + PostgreSQL read/write for top5_cache)
# =============================================================================
#
# Initial readiness — populate_top5_for_country / populate_top5_all_countries
#   • Read rows from country_articles filtered by country_code (includes
#     total_location_count; total_source_location_count once that column exists).
#   • score_articles + select_top5; weights come from the function call — use
#     built-in defaults for any weight that is null/NaN (per component).
#   • generate_headline for each top-5 row; REPLACE top5_cache for that country
#     (last_updated on each top-5 row only).
#
# User update — update_country_scoring_db(country_code, weight_* optional)
#   • Same reads; rescored weights passed in (defaults fill nulls per component).
#   • Reuse headline if URL was already in the prior top 5; else generate.
#   • REPLACE top5_cache (last_updated on each row only).
#   • No separate table for weights — callers pass values; nothing else stored.
#
# Connection: obtain a psycopg2 connection (e.g. db.get_connection()).
# =============================================================================
#
# -----------------------------------------------------------------------------
# REFERENCE FOR CONNECTION — which function, params, and return (see implementations below)
# -----------------------------------------------------------------------------
# First-time one country:  populate_top5_for_country(conn, country_code,
#                           weight_intensity=None, weight_richness=None,
#                           weight_locality=None) -> bool
# First-time all countries: populate_top5_all_countries(conn) -> dict[str, bool]
# Rescore one country:      update_country_scoring_db(conn, country_code,
#                           weight_intensity=None, weight_richness=None,
#                           weight_locality=None) -> bool
# Params: conn + country_code + optional weights (null/NaN → 0.40 / 0.30 / 0.30 each).
# populate_top5_for_country: read country_articles (+ country_name from country_status),
#   write top5_cache; True iff ≥5 articles written, else False (cache unchanged if <5).
# update_country_scoring_db: same + reuse headlines for URLs still in top 5;
#   True if top5 written, else False and that country's top5_cache cleared.
# No JSON here; last_updated only on top5_cache rows.
# -----------------------------------------------------------------------------


# Min-max normalization across a series, returns 0 if range is zero
def _normalize(series):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.0, index=series.index)
    return (series - mn) / (mx - mn)


# Compute composite relevancy score per article
# Intensity: tone magnitude + polarity strength
# Richness: theme and person entity count
# Locality: total_source_location_count / total_location_count (from DB columns)
def score_articles(
    df,
    weight_intensity=0.40,
    weight_richness=0.30,
    weight_locality=0.30,
):
    df = df.copy()

    tone_abs = df["tone"].abs().fillna(0)
    polarity = df["polarity"].fillna(0)
    df["intensity"] = _normalize(0.6 * tone_abs + 0.4 * polarity)

    richness_raw = df["theme_count"].fillna(0) + df["person_count"].fillna(0)
    df["richness"] = _normalize(richness_raw)

    total_loc = df["total_location_count"].fillna(0)
    src_loc = df["total_source_location_count"].fillna(0)
    loc_density = (src_loc / total_loc).where(total_loc > 0, 0.0)
    df["locality"] = _normalize(loc_density)

    df["relevancy_score"] = (
        weight_intensity * df["intensity"] +
        weight_richness * df["richness"] +
        weight_locality * df["locality"]
    ).round(4)

    return df


def _slug_is_purely_numeric(s):
    return bool(s) and re.sub(r"\s+", "", s).isdigit()


def _first_person(persons):
    """First named person from a DB text field (semicolon- or comma-separated blocks)."""
    if persons is None:
        return ""
    if not isinstance(persons, str):
        try:
            if pd.isna(persons):
                return ""
        except (TypeError, ValueError):
            pass
    s = str(persons).strip()
    if not s:
        return ""
    first_block = s.split(";")[0].strip()
    first_name = first_block.split(",")[0].strip()
    return first_name.title() if first_name else ""


def _first_theme_clean(themes):
    if themes is None:
        return ""
    if not isinstance(themes, str):
        try:
            if pd.isna(themes):
                return ""
        except (TypeError, ValueError):
            pass
    if not str(themes).strip():
        return ""
    return str(themes).split(";")[0].replace("_", " ").strip().title()


# Display headline: Tier 1 from URL slug; Tier 2 from persons / themes / both / generic.
def generate_headline(url, source_name, themes, persons=None):
    # Tier 1: last path segment, hyphens to spaces, title case; accept if len > 15 & not purely numeric
    try:
        path = re.sub(r"https?://[^/]+", "", str(url)).rstrip("/")
        slug = path.split("/")[-1]
        slug = re.sub(r"[-_]", " ", slug)
        slug = re.sub(r"\.\w{2,4}$", "", slug)
        slug = re.sub(r"[^a-zA-Z0-9 ]", "", slug).strip()
        if len(slug) > 15 and not _slug_is_purely_numeric(slug):
            return slug.title()
    except Exception:
        pass

    # Tier 2: person / theme / "Person — Theme" / Breaking News
    first_person = _first_person(persons)
    first_theme = _first_theme_clean(themes)
    if first_person and first_theme:
        return f"{first_person} — {first_theme}"
    if first_person:
        return first_person
    if first_theme:
        return first_theme
    return "Breaking News"


# Select top 5 articles: slots 1-3 enforce theme diversity, 4-5 by score
def select_top5(df):
    df = df.sort_values("relevancy_score", ascending=False).reset_index(drop=True)

    selected = []
    seen_themes = set()

    for _, row in df.iterrows():
        if len(selected) >= 3:
            break
        top_theme = row["themes"].split(";")[0] if row.get("themes") else ""
        if top_theme not in seen_themes:
            selected.append(row)
            seen_themes.add(top_theme)

    used_urls = {r["url"] for r in selected}
    for _, row in df.iterrows():
        if len(selected) >= 5:
            break
        if row["url"] not in used_urls:
            selected.append(row)
            used_urls.add(row["url"])

    return selected


DEFAULT_WEIGHT_INTENSITY = 0.40
DEFAULT_WEIGHT_RICHNESS = 0.30
DEFAULT_WEIGHT_LOCALITY = 0.30


def _default_weights() -> tuple[float, float, float]:
    return (DEFAULT_WEIGHT_INTENSITY, DEFAULT_WEIGHT_RICHNESS, DEFAULT_WEIGHT_LOCALITY)


def _weight_is_missing(w: Any) -> bool:
    if w is None:
        return True
    try:
        if pd.isna(w):
            return True
    except (TypeError, ValueError):
        pass
    return False


def resolve_weights(
    weight_intensity: Optional[float] = None,
    weight_richness: Optional[float] = None,
    weight_locality: Optional[float] = None,
) -> tuple[float, float, float]:
    """Use default for each weight component when that argument is null/NaN."""
    di, dr, dl = _default_weights()
    wi = di if _weight_is_missing(weight_intensity) else float(weight_intensity)
    wr = dr if _weight_is_missing(weight_richness) else float(weight_richness)
    wl = dl if _weight_is_missing(weight_locality) else float(weight_locality)
    return (wi, wr, wl)


def fetch_country_articles_for_scoring(conn, country_code: str) -> pd.DataFrame:
    """
    Load article rows for one country from country_articles (filtered by
    country_code). Locality uses total_source_location_count and
    total_location_count on each row — add total_source_location_count to the
    table when available; until then the query will need that column to exist or
    omit it from your deployed schema.
    """
    sql = """
    SELECT
        ca.url,
        ca.country_code,
        ca.source_name,
        ca.themes,
        ca.persons,
        ca.tone,
        ca.polarity,
        ca.theme_count,
        ca.person_count,
        COALESCE(ca.total_source_location_count, 0)::double precision
            AS total_source_location_count,
        COALESCE(ca.total_location_count, 0)::double precision AS total_location_count
    FROM country_articles ca
    WHERE ca.country_code = %s
    """
    return pd.read_sql_query(sql, conn, params=[country_code])


def resolve_country_name(conn, country_code: str) -> str:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT country_name FROM country_status WHERE country_code = %s",
            (country_code,),
        )
        r = cur.fetchone()
        if r and r.get("country_name"):
            return str(r["country_name"])
    return country_code


def fetch_existing_top5_headlines_by_url(conn, country_code: str) -> dict[str, str]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT url, headline FROM top5_cache WHERE country_code = %s",
            (country_code,),
        )
        rows = cur.fetchall()
    return {str(r["url"]): str(r["headline"]) for r in rows}


def replace_country_top5_cache(conn, country_code: str, rows: list[dict[str, Any]]) -> None:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM top5_cache WHERE country_code = %s", (country_code,))
        if not rows:
            conn.commit()
            return
        tuples = [
            (
                r["country_code"],
                r["rank"],
                r["url"],
                r["headline"],
                r["relevancy_score"],
                r["country_name"],
                r["source_name"],
                r["themes"],
                r["last_updated"],
                r["is_cached"],
            )
            for r in rows
        ]
        execute_values(
            cur,
            """
            INSERT INTO top5_cache (
                country_code, rank, url, headline, relevancy_score,
                country_name, source_name, themes, last_updated, is_cached
            ) VALUES %s
            """,
            tuples,
        )
    conn.commit()


def _rows_for_top5(
    country_code: str,
    country_name: str,
    top5_rows: list,
    headlines_by_url: dict[str, str],
) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    out: list[dict[str, Any]] = []
    for i, row in enumerate(top5_rows):
        rank = i + 1
        url = str(row["url"])
        headline = headlines_by_url.get(url)
        if headline is None:
            headline = generate_headline(
                row["url"],
                row.get("source_name"),
                row.get("themes"),
                persons=row.get("persons"),
            )
        out.append(
            {
                "country_code": country_code,
                "rank": rank,
                "url": url,
                "headline": headline,
                "relevancy_score": float(row["relevancy_score"]),
                "country_name": country_name,
                "source_name": row.get("source_name"),
                "themes": row.get("themes"),
                "last_updated": now,
                "is_cached": False,
            }
        )
    return out


def populate_top5_for_country(
    conn,
    country_code: str,
    weight_intensity: Optional[float] = None,
    weight_richness: Optional[float] = None,
    weight_locality: Optional[float] = None,
) -> bool:
    """
    Score articles for one country; null/NaN weights use defaults (per component).
    Generate headlines for all top-5 rows; replace top5_cache (per-row last_updated).
    Returns False if fewer than five articles (does not clear existing cache).
    """
    df = fetch_country_articles_for_scoring(conn, country_code)
    if len(df) < 5:
        return False
    wi, wr, wl = resolve_weights(weight_intensity, weight_richness, weight_locality)
    scored = score_articles(
        df, weight_intensity=wi, weight_richness=wr, weight_locality=wl
    )
    top5 = select_top5(scored)
    if not top5:
        return False
    country_name = resolve_country_name(conn, country_code)
    rows = _rows_for_top5(country_code, country_name, top5, {})
    replace_country_top5_cache(conn, country_code, rows)
    return True


def populate_top5_all_countries(conn) -> dict[str, bool]:
    """
    Run populate_top5_for_country for every distinct country_code in
    country_articles (each must have at least five rows or it is skipped).
    """
    codes = pd.read_sql_query(
        "SELECT DISTINCT country_code FROM country_articles",
        conn,
    )["country_code"].tolist()
    result: dict[str, bool] = {}
    for cc in codes:
        result[str(cc)] = populate_top5_for_country(conn, str(cc))
    return result


def update_country_scoring_db(
    conn,
    country_code: str,
    weight_intensity: Optional[float] = None,
    weight_richness: Optional[float] = None,
    weight_locality: Optional[float] = None,
) -> bool:
    """
    Rescore one country with weights from the call (null/NaN → defaults per component).
    Replace top5_cache (each row carries last_updated); reuse headlines for URLs
    already in the previous top 5.
    Returns False if fewer than five articles (top5_cache for this country cleared).
    """
    wi, wr, wl = resolve_weights(weight_intensity, weight_richness, weight_locality)
    country_name = resolve_country_name(conn, country_code)
    old_headlines = fetch_existing_top5_headlines_by_url(conn, country_code)
    df = fetch_country_articles_for_scoring(conn, country_code)
    if len(df) < 5:
        replace_country_top5_cache(conn, country_code, [])
        return False
    scored = score_articles(
        df,
        weight_intensity=wi,
        weight_richness=wr,
        weight_locality=wl,
    )
    top5 = select_top5(scored)
    if not top5:
        replace_country_top5_cache(conn, country_code, [])
        return False
    merged: dict[str, str] = {}
    for row in top5:
        u = str(row["url"])
        if u in old_headlines:
            merged[u] = old_headlines[u]
        else:
            merged[u] = generate_headline(
                row["url"],
                row.get("source_name"),
                row.get("themes"),
                persons=row.get("persons"),
            )
    rows = _rows_for_top5(country_code, country_name, top5, merged)
    replace_country_top5_cache(conn, country_code, rows)
    return True


"""
# Build top5 cache dict keyed by country code, skips countries with < 5 articles
def build_top5_cache(country_articles_df):
    cache = {}
    now = datetime.now(timezone.utc).isoformat()

    for country_code, group in country_articles_df.groupby("country_code"):
        if len(group) < 5:
            continue

        scored = score_articles(group)
        top5 = select_top5(scored)

        cache[country_code] = [
            {
                "rank": i + 1,
                "url": row["url"],
                "headline": generate_headline(
                    row["url"],
                    row.get("source_name"),
                    row.get("themes"),
                    persons=row.get("persons"),
                ),
                "relevancy_score": float(row["relevancy_score"]),
                "source_name": row.get("source_name"),
                "themes": row.get("themes"),
                "last_updated": now,
                "is_cached": False,
            }
            for i, row in enumerate(top5)
        ]

    return cache


def save_cache(cache, path=CACHE_PATH):
    with open(path, "w") as f:
        json.dump(cache, f)


def load_cache(path=CACHE_PATH):
    with open(path) as f:
        return json.load(f)
"""