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
import math
from utils import scorer

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


class FakeAsyncCursor:
    def __init__(self, *, rows=None, row=None):
        self.rows = rows or []
        self.row = row
        self.executed = []
        self.executemany_calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def execute(self, sql, params=None):
        self.executed.append((sql, params))

    async def executemany(self, sql, params_seq):
        self.executemany_calls.append((sql, params_seq))

    async def fetchall(self):
        return self.rows

    async def fetchone(self):
        return self.row


class FakeAsyncConnection:
    def __init__(self, *, rows=None, row=None):
        self.cursor_obj = FakeAsyncCursor(rows=rows, row=row)
        self.cursor_kwargs = []
        self.commit_count = 0

    def cursor(self, **kwargs):
        self.cursor_kwargs.append(kwargs)
        return self.cursor_obj

    async def commit(self):
        self.commit_count += 1


def article_df(rows=None):
    base_rows = rows or [
        {
            "url": "https://news.example.com/world-leaders-meet-for-climate-summit",
            "country_code": "US",
            "source_name": "news.example.com",
            "themes": "CLIMATE;POLITICS",
            "persons": "jane doe;john smith",
            "tone": -8.0,
            "polarity": 7.0,
            "theme_count": 5,
            "person_count": 2,
            "total_source_location_count": 4,
            "total_location_count": 8,
            "page_title": "Climate Summit Opens",
            "country_name": "United States",
        },
        {
            "url": "https://news.example.com/economy-growth-report-shows-progress",
            "country_code": "US",
            "source_name": "news.example.com",
            "themes": "ECONOMY;BUSINESS",
            "persons": "alex rivera",
            "tone": 2.0,
            "polarity": 3.0,
            "theme_count": 3,
            "person_count": 1,
            "total_source_location_count": 2,
            "total_location_count": 4,
            "page_title": None,
            "country_name": "United States",
        },
        {
            "url": "https://news.example.com/health-officials-expand-services",
            "country_code": "US",
            "source_name": "news.example.com",
            "themes": "HEALTH",
            "persons": None,
            "tone": None,
            "polarity": None,
            "theme_count": None,
            "person_count": None,
            "total_source_location_count": 0,
            "total_location_count": 0,
            "page_title": None,
            "country_name": "United States",
        },
    ]
    return pd.DataFrame(base_rows)


def top5_df():
    return pd.DataFrame(
        [
            {"url": "u1", "themes": "A;X", "relevancy_score": 0.99, "page_title": None, "source_name": "s", "persons": None},
            {"url": "u2", "themes": "A;Y", "relevancy_score": 0.98, "page_title": None, "source_name": "s", "persons": None},
            {"url": "u3", "themes": "B", "relevancy_score": 0.97, "page_title": None, "source_name": "s", "persons": None},
            {"url": "u4", "themes": "B;Z", "relevancy_score": 0.96, "page_title": None, "source_name": "s", "persons": None},
            {"url": "u5", "themes": "C", "relevancy_score": 0.95, "page_title": None, "source_name": "s", "persons": None},
            {"url": "u6", "themes": "D", "relevancy_score": 0.10, "page_title": None, "source_name": "s", "persons": None},
        ]
    )


def test_resolve_weights_uses_defaults_for_missing_values():
    assert scorer.resolve_weights() == (
        scorer.DEFAULT_WEIGHT_INTENSITY,
        scorer.DEFAULT_WEIGHT_RICHNESS,
        scorer.DEFAULT_WEIGHT_LOCALITY,
    )

    assert scorer.resolve_weights(0.7, None, math.nan) == (
        0.7,
        scorer.DEFAULT_WEIGHT_RICHNESS,
        scorer.DEFAULT_WEIGHT_LOCALITY,
    )


def test_score_articles_normalizes_equal_values_to_zero():
    rows = [
        {
            "tone": 1.0,
            "polarity": 1.0,
            "theme_count": 2,
            "person_count": 3,
            "total_source_location_count": 1,
            "total_location_count": 2,
        },
        {
            "tone": 1.0,
            "polarity": 1.0,
            "theme_count": 2,
            "person_count": 3,
            "total_source_location_count": 1,
            "total_location_count": 2,
        },
    ]

    scored = scorer.score_articles(pd.DataFrame(rows))

    assert scored["intensity"].tolist() == [0.0, 0.0]
    assert scored["richness"].tolist() == [0.0, 0.0]
    assert scored["locality"].tolist() == [0.0, 0.0]
    assert scored["relevancy_score"].tolist() == [0.0, 0.0]


def test_select_top5_prioritizes_theme_diversity_then_score():
    selected = scorer.select_top5(top5_df())

    assert len(selected) == 5
    assert [row["url"] for row in selected] == ["u1", "u3", "u5", "u2", "u4"]
    assert len({row["url"] for row in selected}) == 5
    assert [row["themes"].split(";")[0] for row in selected[:3]] == ["A", "B", "C"]


def test_generate_headline_prefers_slug_then_structured_fallbacks():
    assert (
        scorer.generate_headline(
            "https://example.com/world-leaders-meet-for-climate-summit",
            "example.com",
            "CLIMATE_POLICY",
            persons="jane doe",
        )
        == "World Leaders Meet For Climate Summit"
    )
    assert scorer.generate_headline("https://example.com/12345", "example.com", "CLIMATE_POLICY", "jane doe") == "Jane Doe — Climate Policy"
    assert scorer.generate_headline("https://example.com/a", "example.com", None, "jane doe") == "Jane Doe"
    assert scorer.generate_headline("https://example.com/a", "example.com", "PUBLIC_HEALTH", None) == "Public Health"
    assert scorer.generate_headline("https://example.com/a", "example.com", None, None) == "Breaking News"


def test_rows_for_top5_reuses_headlines_and_falls_back_to_page_title_or_generated():
    rows = scorer._rows_for_top5(
        "US",
        "United States",
        [
            pd.Series(
                {
                    "url": "https://example.com/existing",
                    "relevancy_score": 0.9,
                    "source_name": "example.com",
                    "themes": "POLITICS",
                    "persons": "old person",
                    "page_title": "Ignored Page Title",
                }
            ),
            pd.Series(
                {
                    "url": "https://example.com/new",
                    "relevancy_score": 0.8,
                    "source_name": "example.com",
                    "themes": "ECONOMY",
                    "persons": "new person",
                    "page_title": "Fresh Page Title",
                }
            ),
            pd.Series(
                {
                    "url": "https://example.com/123",
                    "relevancy_score": 0.7,
                    "source_name": "example.com",
                    "themes": "HEALTH_POLICY",
                    "persons": "casey lee",
                    "page_title": None,
                }
            ),
        ],
        {"https://example.com/existing": "Existing Headline"},
    )

    assert [row["rank"] for row in rows] == [1, 2, 3]
    assert rows[0]["headline"] == "Existing Headline"
    assert rows[1]["headline"] == "Fresh Page Title"
    assert rows[2]["headline"] == "Casey Lee — Health Policy"
    assert rows[0]["country_code"] == "US"
    assert rows[0]["country_name"] == "United States"
    assert rows[0]["is_cached"] is False
    assert isinstance(rows[0]["last_updated"], datetime)
    assert rows[0]["last_updated"].tzinfo is not None


@pytest.mark.asyncio
async def test_fetch_country_articles_for_scoring_executes_filtered_query_and_returns_dataframe():
    conn = FakeAsyncConnection(
        rows=[
            {
                "url": "https://example.com/story",
                "country_code": "US",
                "source_name": "example.com",
                "themes": "POLITICS",
            }
        ]
    )

    df = await scorer.fetch_country_articles_for_scoring(conn, "US")

    sql, params = conn.cursor_obj.executed[0]
    assert "FROM country_articles ca" in sql
    assert "WHERE ca.country_code = %s" in sql
    assert params == ("US",)
    assert df.to_dict("records") == conn.cursor_obj.rows


@pytest.mark.asyncio
async def test_resolve_country_name_returns_db_name_or_country_code():
    conn = FakeAsyncConnection(row={"country_name": "United States"})

    assert await scorer.resolve_country_name(conn, "US") == "United States"
    assert conn.cursor_obj.executed[0][1] == ("US",)

    missing_conn = FakeAsyncConnection(row=None)
    assert await scorer.resolve_country_name(missing_conn, "ZZ") == "ZZ"


@pytest.mark.asyncio
async def test_fetch_existing_top5_headlines_by_url_returns_url_map():
    conn = FakeAsyncConnection(
        rows=[
            {"url": "https://example.com/a", "headline": "A"},
            {"url": "https://example.com/b", "headline": "B"},
        ]
    )

    result = await scorer.fetch_existing_top5_headlines_by_url(conn, "US")

    assert result == {"https://example.com/a": "A", "https://example.com/b": "B"}
    assert conn.cursor_obj.executed[0][1] == ("US",)


@pytest.mark.asyncio
async def test_replace_country_top5_cache_deletes_and_commits_when_empty():
    conn = FakeAsyncConnection()

    await scorer.replace_country_top5_cache(conn, "US", [])

    sql, params = conn.cursor_obj.executed[0]
    assert "DELETE FROM top5_cache WHERE country_code = %s" in sql
    assert params == ("US",)
    assert conn.cursor_obj.executemany_calls == []
    assert conn.commit_count == 1


@pytest.mark.asyncio
async def test_replace_country_top5_cache_inserts_rows_and_commits():
    conn = FakeAsyncConnection()
    rows = [
        {
            "country_code": "US",
            "rank": 1,
            "url": "https://example.com/a",
            "headline": "A",
            "relevancy_score": 0.9,
            "country_name": "United States",
            "source_name": "example.com",
            "themes": "POLITICS",
            "last_updated": datetime(2026, 1, 1),
            "is_cached": False,
        }
    ]

    await scorer.replace_country_top5_cache(conn, "US", rows)

    assert len(conn.cursor_obj.executed) == 1
    assert len(conn.cursor_obj.executemany_calls) == 1
    insert_sql, tuples = conn.cursor_obj.executemany_calls[0]
    assert "INSERT INTO top5_cache" in insert_sql
    assert tuples == [
        (
            "US",
            1,
            "https://example.com/a",
            "A",
            0.9,
            "United States",
            "example.com",
            "POLITICS",
            datetime(2026, 1, 1),
            False,
        )
    ]
    assert conn.commit_count == 1


@pytest.mark.asyncio
async def test_populate_top5_all_countries_scores_only_countries_with_enough_articles(monkeypatch):
    writes = []
    rows = []
    for country_code, country_name, count in [("US", "United States", 5), ("CA", "Canada", 4)]:
        for i in range(count):
            rows.append(
                {
                    "url": f"https://example.com/{country_code}/{i}",
                    "country_code": country_code,
                    "country_name": country_name,
                    "source_name": "example.com",
                    "themes": f"THEME_{i}",
                    "persons": None,
                    "tone": float(i),
                    "polarity": float(i),
                    "theme_count": i + 1,
                    "person_count": 0,
                    "total_source_location_count": i + 1,
                    "total_location_count": 10,
                    "page_title": f"{country_code} Story {i}",
                }
            )

    async def fake_fetch(conn):
        return pd.DataFrame(rows)

    async def fake_replace(conn, country_code, cache_rows):
        writes.append((country_code, cache_rows))

    monkeypatch.setattr(scorer, "fetch_country_articles_for_scoring", fake_fetch)
    monkeypatch.setattr(scorer, "replace_country_top5_cache", fake_replace)

    result = await scorer.populate_top5_all_countries(object())

    assert result == {"CA": False, "US": True}
    assert len(writes) == 1
    assert writes[0][0] == "US"
    assert len(writes[0][1]) == 5


@pytest.mark.asyncio
async def test_update_country_scoring_db_clears_cache_when_country_has_too_few_articles(monkeypatch):
    writes = []

    async def fake_resolve_name(conn, country_code):
        return "United States"

    async def fake_old_headlines(conn, country_code):
        return {}

    async def fake_fetch(conn, country_code):
        return article_df().head(3)

    async def fake_replace(conn, country_code, rows):
        writes.append((country_code, rows))

    monkeypatch.setattr(scorer, "resolve_country_name", fake_resolve_name)
    monkeypatch.setattr(scorer, "fetch_existing_top5_headlines_by_url", fake_old_headlines)
    monkeypatch.setattr(scorer, "fetch_country_articles_for_scoring", fake_fetch)
    monkeypatch.setattr(scorer, "replace_country_top5_cache", fake_replace)

    assert await scorer.update_country_scoring_db(object(), "US") is False
    assert writes == [("US", [])]


@pytest.mark.asyncio
async def test_update_country_scoring_db_reuses_old_headlines_and_writes_new_rows(monkeypatch):
    writes = []
    rows = []
    for i in range(5):
        rows.append(
            {
                "url": f"https://example.com/story-{i}",
                "country_code": "US",
                "country_name": "United States",
                "source_name": "example.com",
                "themes": f"THEME_{i}",
                "persons": "jane doe",
                "tone": float(i),
                "polarity": float(i),
                "theme_count": i + 1,
                "person_count": 1,
                "total_source_location_count": i + 1,
                "total_location_count": 10,
                "page_title": f"Page Title {i}",
            }
        )

    async def fake_resolve_name(conn, country_code):
        return "United States"

    async def fake_old_headlines(conn, country_code):
        return {"https://example.com/story-4": "Previously Cached"}

    async def fake_fetch(conn, country_code):
        return pd.DataFrame(rows)

    async def fake_replace(conn, country_code, cache_rows):
        writes.append((country_code, cache_rows))

    monkeypatch.setattr(scorer, "resolve_country_name", fake_resolve_name)
    monkeypatch.setattr(scorer, "fetch_existing_top5_headlines_by_url", fake_old_headlines)
    monkeypatch.setattr(scorer, "fetch_country_articles_for_scoring", fake_fetch)
    monkeypatch.setattr(scorer, "replace_country_top5_cache", fake_replace)

    assert await scorer.update_country_scoring_db(
        object(),
        "US",
        weight_intensity=0.5,
        weight_richness=0.25,
        weight_locality=0.25,
    ) is True

    assert len(writes) == 1
    country_code, cache_rows = writes[0]
    assert country_code == "US"
    assert len(cache_rows) == 5
    headlines_by_url = {row["url"]: row["headline"] for row in cache_rows}
    assert headlines_by_url["https://example.com/story-4"] == "Previously Cached"
    assert "Page Title" in headlines_by_url["https://example.com/story-3"]