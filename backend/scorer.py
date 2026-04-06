import json
import re
from datetime import datetime, timezone

import pandas as pd

CACHE_PATH = "top5_cache.json"


# Min-max normalization across a series, returns 0 if range is zero
def _normalize(series):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.0, index=series.index)
    return (series - mn) / (mx - mn)


# Compute composite relevancy score per article
# Intensity (40%): tone magnitude + polarity strength
# Richness  (30%): theme and person entity count
# Locality  (30%): fraction of location mentions for this country
def score_articles(df):
    df = df.copy()

    tone_abs = df["tone"].abs().fillna(0)
    polarity = df["polarity"].fillna(0)
    df["intensity"] = _normalize(0.6 * tone_abs + 0.4 * polarity)

    richness_raw = df["theme_count"].fillna(0) + df["person_count"].fillna(0)
    df["richness"] = _normalize(richness_raw)

    loc_density = df.apply(
        lambda r: r["location_count"] / r["total_location_count"]
        if r["total_location_count"] > 0 else 0.0,
        axis=1,
    )
    df["locality"] = _normalize(loc_density)

    df["relevancy_score"] = (
        0.40 * df["intensity"] +
        0.30 * df["richness"] +
        0.30 * df["locality"]
    ).round(4)

    return df


# Generate display headline from URL slug
# Tier 1: readable slug extracted from URL path
# Tier 2: fallback to source name + top theme
def generate_headline(url, source_name, themes):
    try:
        path = re.sub(r"https?://[^/]+", "", str(url)).rstrip("/")
        slug = path.split("/")[-1]
        slug = re.sub(r"[-_]", " ", slug)
        slug = re.sub(r"\.\w{2,4}$", "", slug)
        slug = re.sub(r"[^a-zA-Z0-9 ]", "", slug).strip()
        if len(slug) > 8:
            return slug.title()
    except Exception:
        pass

    top_theme = themes.split(";")[0].replace("_", " ").title() if themes else ""
    src = source_name or "News"
    return f"{src}: {top_theme}" if top_theme else src


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
                    row["url"], row.get("source_name"), row.get("themes")
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
