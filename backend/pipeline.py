import io
import zipfile
from datetime import datetime, timezone

import pandas as pd
import requests

from utils.daily import get_update, GKG_COLUMNS
from parse_csv import (
    assign_countries,
    count_location_mentions,
    count_semicolon_items,
    get_country_counts,
    parse_date,
    parse_tone,
)
from scorer import build_top5_cache, save_cache


# Download latest GKG file from GDELT update manifest and return as DataFrame
def download_gkg():
    links = get_update()
    gkg_url = next((l for l in links if "gkg" in l.lower()), links[2])

    resp = requests.get(gkg_url, timeout=60)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        with z.open(z.namelist()[0]) as f:
            df = pd.read_csv(
                f, sep="\t", names=GKG_COLUMNS, dtype=str, on_bad_lines="skip"
            )

    return df


# Quality filter: web sources only, drop rows missing required fields, dedupe URLs
def filter_gkg(df):
    df = df[df["V2SOURCECOLLECTIONIDENTIFIER"].str.strip() == "1"]

    required = ["V1LOCATIONS", "V1THEMES", "V1.5TONE", "V2DOCUMENTIDENTIFIER"]
    for field in required:
        df = df[df[field].notna() & (df[field].str.strip() != "")]

    df = df.drop_duplicates(subset=["V2DOCUMENTIDENTIFIER"])
    return df


# Build country-article rows from filtered GKG DataFrame
# Reuses parse_csv helpers for country assignment and field computation
def build_country_articles(df):
    rows = []

    for _, row in df.iterrows():
        locations_raw = row.get("V1LOCATIONS", "")
        country_counts = get_country_counts(locations_raw)
        assignments = assign_countries(country_counts)
        if not assignments:
            continue

        tone, positive_score, negative_score, polarity = parse_tone(row.get("V1.5TONE", ""))
        theme_count = count_semicolon_items(row.get("V1THEMES", ""))
        person_count = count_semicolon_items(row.get("V1PERSONS", ""))

        url = row.get("V2DOCUMENTIDENTIFIER", "")
        themes = row.get("V1THEMES", "") or None
        persons = row.get("V1PERSONS", "") or None
        source_name = row.get("V2SOURCECOMMONNAME", "") or None
        pub_date = parse_date(row.get("V2.1DATE", ""))

        for country_code, confidence in assignments:
            location_count, total_location_count = count_location_mentions(
                locations_raw, country_code
            )
            rows.append({
                "url": url,
                "country_code": country_code,
                "country_confidence": confidence,
                "source_name": source_name,
                "pub_date": pub_date,
                "themes": themes,
                "persons": persons,
                "tone": tone,
                "positive_score": positive_score,
                "negative_score": negative_score,
                "polarity": polarity,
                "theme_count": theme_count,
                "person_count": person_count,
                "location_count": location_count,
                "total_location_count": total_location_count,
            })

    return pd.DataFrame(rows)


# Full pipeline: download → filter → score → save JSON cache
def run_pipeline():
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] Fetching latest GDELT GKG...")

    raw_df = download_gkg()
    print(f"  {len(raw_df)} rows downloaded")

    filtered_df = filter_gkg(raw_df)
    print(f"  {len(filtered_df)} rows after quality filter")

    country_df = build_country_articles(filtered_df)
    print(f"  {len(country_df)} country-article rows built")

    cache = build_top5_cache(country_df)
    print(f"  {len(cache)} countries scored")

    save_cache(cache)
    print("  Saved top5_cache.json")


if __name__ == "__main__":
    run_pipeline()
