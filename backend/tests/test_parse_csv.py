import pytest
from datetime import datetime, timezone
from utils.parse_csv import insert_raw_articles


def make_db_row(url="http://test.com/article", country_code="US"):
    return (
        url,
        country_code,
        1.0,
        "cnn.com",
        datetime.now(timezone.utc),
        datetime.now(timezone.utc),
        "HEALTH;ECON",
        "john doe",
        "WHO",
        "1#New York#US#USNY#40.7#-74.0#456",
        "-2.0,1.0,3.0,4.0",
        "",
    )


@pytest.mark.asyncio
async def test_insert_raw_articles(conn):
    await insert_raw_articles(conn, [make_db_row(url="http://test.com/insert-test")])

    async with conn.cursor() as cur:
        await cur.execute("SELECT url, country_code FROM raw_articles WHERE url = %s", ("http://test.com/insert-test",))
        row = await cur.fetchone()

    assert row is not None
    assert row[0] == "http://test.com/insert-test"
    assert row[1] == "US"


@pytest.mark.asyncio
async def test_insert_raw_articles_upsert(conn):
    url = "http://test.com/upsert-test"
    await insert_raw_articles(conn, [make_db_row(url=url)])

    updated = (
        url, "US", 0.9, "cnn.com",
        datetime.now(timezone.utc), datetime.now(timezone.utc),
        "HEALTH", None, None,
        "1#New York#US#USNY#40.7#-74.0#456",
        "-5.0,2.0,7.0,9.0", "",
    )
    await insert_raw_articles(conn, [updated])

    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT country_confidence FROM raw_articles WHERE url = %s AND country_code = 'US'",
            (url,)
        )
        result = await cur.fetchone()

    assert result[0] == pytest.approx(0.9)


@pytest.mark.asyncio
async def test_insert_raw_articles_multiple_countries(conn):
    url = "http://test.com/multi-country"
    rows = [make_db_row(url=url, country_code="US"), make_db_row(url=url, country_code="UK")]
    await insert_raw_articles(conn, rows)

    async with conn.cursor() as cur:
        await cur.execute("SELECT country_code FROM raw_articles WHERE url = %s ORDER BY country_code", (url,))
        results = await cur.fetchall()

    codes = [r[0] for r in results]
    assert "UK" in codes
    assert "US" in codes