import csv
from collections import Counter
from datetime import datetime, timezone
from utils.daily import get_update, parse_gkg
from psycopg import AsyncConnection
from dotenv import load_dotenv
from lxml import etree
from psycopg.rows import dict_row
from collections import defaultdict

import pandas as pd
import re

load_dotenv()

DB_URL = "postgresql://localhost/worldwidenews"
UPDATE_BATCH = datetime.now(timezone.utc)


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def get_country_counts(locations_raw):
    counts = Counter()
    for entry in locations_raw.split(";"):
        parts = entry.split("#")
        if len(parts) >= 3 and parts[2].strip():
            counts[parts[2].strip()] += 1
    return counts



def parse_tone(tone_raw):
    if not tone_raw:
        return None, None, None, None
    parts = tone_raw.split(",")
    try:
        tone = float(parts[0]) if len(parts) > 0 else None
        positive = float(parts[1]) if len(parts) > 1 else None
        negative = float(parts[2]) if len(parts) > 2 else None
        polarity = float(parts[3]) if len(parts) > 3 else None
        return tone, positive, negative, polarity
    except (ValueError, IndexError):
        return None, None, None, None


def count_semicolon_items(s):
    if not s:
        return 0
    return len([x for x in s.split(";") if x.strip()])


def count_location_mentions(locations_raw, country_code):
    if not locations_raw:
        return 0, 0
    entries = [e for e in locations_raw.split(";") if e.strip()]
    total = len(entries)
    country_count = sum(
        1 for e in entries
        if len(e.split("#")) >= 3 and e.split("#")[2].strip() == country_code
    )
    return country_count, total


def open_csv(filepath):
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            f = open(filepath, newline="", encoding=encoding)
            f.read(1024)
            f.seek(0)
            return f
        except (UnicodeDecodeError, ValueError):
            f.close()
    raise ValueError(f"Could not read {filepath} with any known encoding")


async def load_csv(stream):
    raw_rows = []
    seen_urls = set()

    async for row in stream:
        source_collection = row.get("V2SOURCECOLLECTIONIDENTIFIER", "").strip()
        locations = row.get("V1LOCATIONS", "").strip()
        themes = row.get("V1THEMES", "").strip()
        tone = row.get("V1.5TONE", "").strip()
        url = row.get("V2DOCUMENTIDENTIFIER", "").strip()
        extras = row.get("V2EXTRASXML").strip()

        if source_collection != "1":
            continue
        if not locations or not themes or not tone:
            continue
        if not url or url in seen_urls:
            continue

        seen_urls.add(url)

        raw_rows.append({
            "url": url,
            "source_name": row.get("V2SOURCECOMMONNAME", "").strip() or None,
            "pub_date": parse_date(row.get("V2.1DATE", "")),
            "themes": themes,
            "persons": row.get("V1PERSONS", "").strip() or None,
            "organizations": row.get("V1ORGANIZATIONS", "").strip() or None,
            "locations_raw": locations,
            "tone_raw": tone,
            "extras": extras
        })
        
        

    return raw_rows

async def get_mappings (conn: AsyncConnection):
    dictionary = defaultdict()

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT domain_name, country_code FROM country_mappings")
        rows = await cur.fetchall()
        
        for row in rows:
            dictionary[row["domain_name"]] = row["country_code"]

    return dictionary

# source_name to country_code
def assign_country(source_name, mapping_rows):
    country_code = mapping_rows[source_name] if source_name in mapping_rows else None

    if (country_code is not None): return country_code

    TLD_TO_COUNTRY = {
        # North & South America
        'us': 'US', 'ca': 'CA', 'mx': 'MX', 'br': 'BR', 'ar': 'AR', 
        'cl': 'CL', 'co': 'CO', 'pe': 'PE',
        
        # Europe
        'uk': 'GB', 'de': 'DE', 'fr': 'FR', 'it': 'IT', 'es': 'ES', 
        'nl': 'NL', 'be': 'BE', 'ch': 'CH', 'se': 'SE', 'no': 'NO', 
        'dk': 'DK', 'fi': 'FI', 'pl': 'PL', 'ie': 'IE', 'pt': 'PT', 
        'gr': 'GR', 'ru': 'RU', 'ua': 'UA', 'ro': 'RO',
        
        # Asia & Pacific
        'cn': 'CN', 'jp': 'JP', 'in': 'IN', 'kr': 'KR', 'id': 'ID', 
        'ph': 'PH', 'vn': 'VN', 'th': 'TH', 'my': 'MY', 'sg': 'SG', 
        'tw': 'TW', 'pk': 'PK', 'au': 'AU', 'nz': 'NZ',
        
        # Middle East & Africa
        'za': 'ZA', 'ng': 'NG', 'ke': 'KE', 'eg': 'EG', 'ae': 'AE', 
        'sa': 'SA', 'il': 'IL', 'tr': 'TR', 'ir': 'IR'
    }

    match = re.search(r'\.([a-z]{2})(?:/|$)', source_name)
    
    if (match is not None):
        tld = match.group(1)
        return TLD_TO_COUNTRY[tld] if tld in TLD_TO_COUNTRY else None


    return None

def build_raw_article_rows(raw_rows, mapping_rows):
    result = []
    
    for row in raw_rows:
        country_code = assign_country(row["source_name"], mapping_rows)

        if country_code is None:
            continue

        result.append((
            row["url"],
            country_code,
            1.0,
            row["source_name"],
            row["pub_date"],
            UPDATE_BATCH,
            row["themes"],
            row["persons"],
            row["organizations"],
            row["locations_raw"],
            row["tone_raw"],
            row["extras"]
        ))
            

    return result


def build_country_article_rows(raw_rows, mapping_rows):

    result = []
    for row in raw_rows:
        country_code = assign_country(row["source_name"], mapping_rows)
        
        if country_code is None:
            print("Unassigned: ", row["source_name"])
            continue

        tone, positive_score, negative_score, polarity = parse_tone(row["tone_raw"])
        theme_count = count_semicolon_items(row["themes"])
        person_count = count_semicolon_items(row["persons"])

        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(f"<root>{row["extras"]}</root>", parser=parser)
        node = root.find("PAGE_TITLE")

        page_title = node.text if node is not None else None

        total_source_location_count, total_location_count = count_location_mentions(
            row["locations_raw"], country_code
        )

        result.append((
            row["url"],
            country_code,
            row["source_name"],
            row["pub_date"],
            UPDATE_BATCH,
            row["themes"],
            row["persons"],
            row["organizations"],
            row["locations_raw"],
            tone,
            positive_score,
            negative_score,
            polarity,
            theme_count,
            person_count,
            total_source_location_count,
            total_location_count,
            page_title
        ))

    return result


async def insert_raw_articles(conn: AsyncConnection, rows):
    sql = """
        INSERT INTO raw_articles (
            url, country_code, country_confidence, source_name,
            pub_date, update_batch, themes, persons, organizations,
            locations_raw, tone_raw, extras
        ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        ON CONFLICT (url, country_code) DO UPDATE SET
            country_confidence = EXCLUDED.country_confidence,
            update_batch = EXCLUDED.update_batch,
            tone_raw = EXCLUDED.tone_raw
    """
    async with conn.cursor() as cur:
        await cur.executemany(sql, rows)

    await conn.commit()


async def insert_country_articles(conn: AsyncConnection, rows):
    sql = """
        INSERT INTO country_articles (
            url, country_code, source_name,
            pub_date, update_batch, themes, persons, organizations,
            locations_raw, tone, positive_score, negative_score, polarity,
            theme_count, person_count, total_source_location_count, total_location_count,
            page_title
        ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        ON CONFLICT (url, country_code) DO UPDATE SET
            tone = EXCLUDED.tone,
            positive_score = EXCLUDED.positive_score,
            negative_score = EXCLUDED.negative_score,
            polarity = EXCLUDED.polarity,
            theme_count = EXCLUDED.theme_count,
            person_count = EXCLUDED.person_count,
            total_source_location_count = EXCLUDED.total_source_location_count,
            total_location_count = EXCLUDED.total_location_count,
            update_batch = EXCLUDED.update_batch,
            page_title = EXCLUDED.page_title
    """
    async with conn.cursor() as cur:
        await cur.executemany(sql, rows)
    await conn.commit()

async def load_mappings (conn: AsyncConnection):
    print("Loading Mappings ... ")

    # In case there are new mappings
    async with conn.cursor() as cur:
        await cur.execute("TRUNCATE TABLE country_mappings;")

    
    rows = []

    with open("data/mapping.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append((row['Domain'], row['FIPS'], row['CountryName']))

    sql = """
        COPY country_mappings (domain_name, country_code, country_name) FROM STDIN
    """

    # This is a big bottleneck from testing.
    # I decided to switch to Postgres COPY which seems to be 
    # very efficent.
    # https://www.psycopg.org/psycopg3/docs/basic/copy.html
    # async with conn.cursor() as cur:
    #     await cur.executemany(sql, rows)

    async with conn.cursor() as cur:
        async with cur.copy(sql) as copy:
            for row in rows:
                await copy.write_row(row)


    await conn.commit()

async def create_tables(conn: AsyncConnection):
    print("Creating Tables ...")
    with open("schema.sql") as f:
        sql = f.read()
    
    async with conn.cursor() as cur:
        await cur.execute(sql)
    
    await conn.commit()


async def refresh_country_status(conn: AsyncConnection):#added this(aryan)
    """Aggregate country_articles into country_status (incl. total source location counts)."""
    sql = """
        INSERT INTO country_status (
            country_code, country_name, last_fresh_update,
            article_count, total_source_location_count, status
        )
        SELECT
            agg.country_code,
            cm.country_name,
            agg.last_fresh_update,
            agg.article_count,
            agg.total_source_location_count,
            'ok'
        FROM (
            SELECT
                ca.country_code,
                MAX(ca.update_batch) AS last_fresh_update,
                COUNT(*)::INTEGER AS article_count,
                COALESCE(SUM(ca.total_source_location_count), 0)::BIGINT
                    AS total_source_location_count
            FROM country_articles ca
            GROUP BY ca.country_code
        ) agg
        LEFT JOIN (
            SELECT country_code, MAX(country_name) AS country_name
            FROM country_mappings
            GROUP BY country_code
        ) cm ON cm.country_code = agg.country_code
        ON CONFLICT (country_code) DO UPDATE SET
            country_name = EXCLUDED.country_name,
            last_fresh_update = EXCLUDED.last_fresh_update,
            article_count = EXCLUDED.article_count,
            total_source_location_count = EXCLUDED.total_source_location_count,
            status = EXCLUDED.status;
    """
    async with conn.cursor() as cur:
        await cur.execute(sql)
    await conn.commit()

async def get_cached ():
    with open_csv("data/gkg.csv") as f:
        reader = csv.DictReader(f)

        for row in reader:
            yield row

async def clear_tables (conn: AsyncConnection):
    async with conn.cursor() as cur:
        await cur.execute("TRUNCATE TABLE country_articles;")
        await cur.execute("TRUNCATE TABLE country_mappings;")
        await cur.execute("TRUNCATE TABLE country_status;")
        await cur.execute("TRUNCATE TABLE raw_articles;")
        await cur.execute("TRUNCATE TABLE top5_cache;")
    
async def refresh_15min (conn: AsyncConnection, cache: bool):
    
    print("Fetching Url")
    _, _, gkg_url = await get_update()
    
    stream = None
    if (cache):
        stream = get_cached()
    else:
        stream = await parse_gkg(gkg_url)

    print("Loading CSV...")
    raw_rows = await load_csv(stream)
    
    print(f"  {len(raw_rows)} rows passed quality filter")

    mappings = await get_mappings(conn)

    raw_article_rows = build_raw_article_rows(raw_rows, mappings)
    print(f"  {len(raw_article_rows)} raw_article rows (after country assignment)")

    country_article_rows = build_country_article_rows(raw_rows, mappings)
    print(f"  {len(country_article_rows)} country_article rows")

    print("Inserting into raw_articles...")
    await insert_raw_articles(conn, raw_article_rows)

    print("Inserting into country_articles...")
    await insert_country_articles(conn, country_article_rows)

    print("Refreshing country_status...")
    await refresh_country_status(conn)

    print("Done.")


if __name__ == "__main__":
    refresh_15min()