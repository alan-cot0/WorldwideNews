import pytest
import pandas as pd
from utils.scorer import (
    score_articles,
    generate_headline,
    select_top5,
    resolve_weights,
    replace_country_top5_cache,
)
from datetime import datetime, timezone


def make_df(n=5, base_tone=1.0, base_polarity=1.0):
    return pd.DataFrame([
        {
            "url": f"http://example.com/article-{i}",
            "source_name": "bbc.co.uk",
            "country_code": "UK",
            "themes": f"THEME{i};ECON",
            "persons": f"person {i}",
            "tone": base_tone * i,
            "polarity": base_polarity * i,
            "theme_count": i + 1,
            "person_count": i,
            "total_source_location_count": float(i),
            "total_location_count": float(i + 2),
            "page_title": None,
            "country_name": "United Kingdom",
        }
        for i in range(1, n + 1)
    ])


def test_score_articles_returns_scores_in_range():
    df = make_df(10)
    result = score_articles(df)
    assert "relevancy_score" in result.columns
    assert (result["relevancy_score"] >= 0.0).all()
    assert (result["relevancy_score"] <= 1.0).all()

def test_score_articles_adds_intensity_richness_locality():
    df = make_df(5)
    result = score_articles(df)
    for col in ("intensity", "richness", "locality"):
        assert col in result.columns

def test_score_articles_custom_weights():
    df = make_df(5)
    result = score_articles(df, weight_intensity=1.0, weight_richness=0.0, weight_locality=0.0)
    assert (result["relevancy_score"] == result["intensity"]).all()

def test_score_articles_all_same_values_no_crash():
    df = pd.DataFrame([{
        "url": f"http://example.com/{i}",
        "source_name": "bbc.co.uk",
        "country_code": "UK",
        "themes": "HEALTH",
        "persons": "person",
        "tone": 1.0,
        "polarity": 1.0,
        "theme_count": 3,
        "person_count": 2,
        "total_source_location_count": 5.0,
        "total_location_count": 10.0,
        "page_title": None,
        "country_name": "United Kingdom",
    } for i in range(5)])
    result = score_articles(df)
    assert not result["relevancy_score"].isna().any()


def test_generate_headline_url_slug():
    url = "https://bbc.co.uk/news/mortgage-affordability-crisis-uk"
    result = generate_headline(url, "bbc.co.uk", "ECON;HEALTH")
    assert result == "Mortgage Affordability Crisis Uk"

def test_generate_headline_slug_too_short_falls_back():
    url = "https://bbc.co.uk/news/abc"
    result = generate_headline(url, "bbc.co.uk", "ECON_TRADE;HEALTH", persons="Jane Doe")
    assert "Jane Doe" in result or "Econ Trade" in result

def test_generate_headline_numeric_slug_falls_back():
    url = "https://focustaiwan.tw/news/202603260012"
    result = generate_headline(url, "focustaiwan.tw", "ELECTION", persons="Ko Lin")
    assert result != "202603260012"
    assert len(result) >= 10

def test_generate_headline_person_and_theme():
    url = "https://example.com/12345"
    result = generate_headline(url, "example.com", "POLITICS_POLICY", persons="John Smith")
    assert "John Smith" in result
    assert "Politics Policy" in result

def test_generate_headline_only_theme():
    url = "https://example.com/12345"
    result = generate_headline(url, "example.com", "ECON_TRADE", persons=None)
    assert result == "Econ Trade"

def test_generate_headline_fallback_breaking_news():
    url = "https://example.com/12345"
    result = generate_headline(url, "example.com", None, persons=None)
    assert result == "Breaking News"


def test_select_top5_returns_five():
    df = score_articles(make_df(10))
    result = select_top5(df)
    assert len(result) == 5

def test_select_top5_top3_unique_themes():
    df = score_articles(make_df(10))
    result = select_top5(df)
    top3_themes = [r["themes"].split(";")[0] for r in result[:3]]
    assert len(set(top3_themes)) == len(top3_themes)

def test_select_top5_fewer_than_five_returns_all():
    df = score_articles(make_df(3))
    result = select_top5(df)
    assert len(result) == 3

def test_select_top5_no_duplicates():
    df = score_articles(make_df(10))
    result = select_top5(df)
    urls = [r["url"] for r in result]
    assert len(urls) == len(set(urls))


def test_resolve_weights_all_none_returns_defaults():
    wi, wr, wl = resolve_weights()
    assert wi == pytest.approx(0.40)
    assert wr == pytest.approx(0.30)
    assert wl == pytest.approx(0.30)

def test_resolve_weights_partial_none():
    wi, wr, wl = resolve_weights(weight_intensity=0.5)
    assert wi == pytest.approx(0.5)
    assert wr == pytest.approx(0.30)
    assert wl == pytest.approx(0.30)

def test_resolve_weights_all_provided():
    wi, wr, wl = resolve_weights(0.5, 0.3, 0.2)
    assert wi == pytest.approx(0.5)
    assert wr == pytest.approx(0.3)
    assert wl == pytest.approx(0.2)


def make_cache_rows(country_code="US", n=5):
    now = datetime.now(timezone.utc)
    return [
        {
            "country_code": country_code,
            "rank": i + 1,
            "url": f"http://example.com/article-{i}",
            "headline": f"Headline {i}",
            "relevancy_score": 0.9 - i * 0.1,
            "country_name": "United States",
            "source_name": "cnn.com",
            "themes": "HEALTH;ECON",
            "last_updated": now,
            "is_cached": False,
        }
        for i in range(n)
    ]

@pytest.mark.asyncio
async def test_replace_country_top5_cache_inserts(conn):
    rows = make_cache_rows("US")
    await replace_country_top5_cache(conn, "US", rows)

    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) FROM top5_cache WHERE country_code = 'US'")
        count = (await cur.fetchone())[0]

    assert count == 5

@pytest.mark.asyncio
async def test_replace_country_top5_cache_replaces_existing(conn):
    await replace_country_top5_cache(conn, "CA", make_cache_rows("CA"))
    await replace_country_top5_cache(conn, "CA", make_cache_rows("CA", n=3))

    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) FROM top5_cache WHERE country_code = 'CA'")
        count = (await cur.fetchone())[0]

    assert count == 3

@pytest.mark.asyncio
async def test_replace_country_top5_cache_empty_clears(conn):
    await replace_country_top5_cache(conn, "IN", make_cache_rows("IN"))
    await replace_country_top5_cache(conn, "IN", [])

    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) FROM top5_cache WHERE country_code = 'IN'")
        count = (await cur.fetchone())[0]

    assert count == 0
