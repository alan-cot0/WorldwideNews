from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from utils.parse_csv import clear_tables, create_tables, load_mappings, refresh_15min
from utils.scorer import (
    DEFAULT_WEIGHT_INTENSITY,
    DEFAULT_WEIGHT_LOCALITY,
    DEFAULT_WEIGHT_RICHNESS,
    fetch_country_articles_for_scoring,
    fetch_existing_top5_headlines_by_url,
    generate_headline,
    populate_top5_all_countries,
    resolve_country_name,
    resolve_weights,
    score_articles,
    select_top5,
    update_country_scoring_db,
)
from dotenv import load_dotenv
import os
from collections import defaultdict
from typing import Optional

from pydantic import BaseModel, Field

from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg.rows import dict_row
import csv
import sys

max_size = sys.maxsize

while True:
    try:
        csv.field_size_limit(max_size)
        break
    except OverflowError:
        max_size = int(max_size / 10)

load_dotenv()

DB_URL = "postgresql://localhost/worldwidenews"

# To not request too much from GDELT
RUN_SETUP = os.getenv("RUN_SETUP").lower() == "true"
USE_CACHE = os.getenv("USE_CACHE").lower() == "true"
CACHE_CSV = os.getenv("CACHE_CSV")

# https://blog.danielclayton.co.uk/posts/database-connections-with-fastapi/

pool = AsyncConnectionPool(
    conninfo=DB_URL,
    min_size=1,
    max_size=4, # Don't make too many
    kwargs={
        "user": os.getenv("USER"),
        "password": os.getenv("PASS")
    },
    open = False
)

async def get_conn():
    async with pool.connection() as conn:
	    yield conn


class ScoringWeights(BaseModel):
    weight_intensity: Optional[float] = Field(default=None, ge=0)
    weight_richness: Optional[float] = Field(default=None, ge=0)
    weight_locality: Optional[float] = Field(default=None, ge=0)


def _normalize_country_code(country_code: str) -> str:
    return country_code.strip().upper()


def _weights_response(
    weight_intensity: Optional[float] = None,
    weight_richness: Optional[float] = None,
    weight_locality: Optional[float] = None,
) -> dict:
    wi, wr, wl = resolve_weights(weight_intensity, weight_richness, weight_locality)
    if wi + wr + wl <= 0:
        raise HTTPException(status_code=422, detail="At least one scoring weight must be greater than 0.")
    return {
        "weight_intensity": wi,
        "weight_richness": wr,
        "weight_locality": wl,
    }


async def _get_top5_cache(conn: AsyncConnection, country_code: str) -> list[dict]:
    sql = """
        SELECT country_code, rank, url, headline,
        relevancy_score, country_name, source_name, themes, last_updated, is_cached
        FROM top5_cache
        WHERE country_code = %s
        ORDER BY rank;
    """

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql, (country_code,))
        return await cur.fetchall()


async def _preview_scored_top5(
    conn: AsyncConnection,
    country_code: str,
    weight_intensity: Optional[float] = None,
    weight_richness: Optional[float] = None,
    weight_locality: Optional[float] = None,
) -> dict:
    weights = _weights_response(weight_intensity, weight_richness, weight_locality)
    df = await fetch_country_articles_for_scoring(conn, country_code)

    if len(df) < 5:
        return {
            "country_code": country_code,
            "updated": False,
            "weights": weights,
            "article_count": len(df),
            "articles": [],
            "message": "At least five articles are required to score a country's top stories.",
        }

    scored = score_articles(
        df,
        weight_intensity=weights["weight_intensity"],
        weight_richness=weights["weight_richness"],
        weight_locality=weights["weight_locality"],
    )
    top5 = select_top5(scored)
    country_name = await resolve_country_name(conn, country_code)
    old_headlines = await fetch_existing_top5_headlines_by_url(conn, country_code)

    articles = []
    for rank, row in enumerate(top5, start=1):
        url = str(row["url"])
        total_locations = float(row.get("total_location_count") or 0)
        source_locations = float(row.get("total_source_location_count") or 0)
        headline = old_headlines.get(url) or row.get("page_title") or generate_headline(
            row["url"],
            row.get("source_name"),
            row.get("themes"),
            persons=row.get("persons"),
        )

        articles.append(
            {
                "country_code": country_code,
                "country_name": country_name,
                "rank": rank,
                "url": url,
                "headline": headline,
                "source_name": row.get("source_name"),
                "themes": row.get("themes"),
                "relevancy_score": float(row["relevancy_score"]),
                "intensity": float(row["intensity"]),
                "richness": float(row["richness"]),
                "locality": float(row["locality"]),
                "total_source_location_count": source_locations,
                "total_location_count": total_locations,
            }
        )

    return {
        "country_code": country_code,
        "country_name": country_name,
        "updated": False,
        "weights": weights,
        "article_count": len(df),
        "articles": articles,
    }
         

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await pool.open()

    if (RUN_SETUP):
        async with pool.connection() as conn:
            await create_tables(conn)
            await clear_tables(conn)
            await load_mappings(conn)
            await refresh_15min(conn, USE_CACHE, CACHE_CSV)
            await populate_top5_all_countries(conn)
        
    yield

    await pool.close()

app = FastAPI(lifespan=lifespan)

allowed_origins = [
    "http://localhost", 
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}


# Not finalized, just something for
# the frontend to play around with

@app.get("/api/countries")
async def get_countries(conn: AsyncConnection = Depends(get_conn)):
    sql = """
        SELECT country_code, rank, url, headline,
        relevancy_score, themes, last_updated
        FROM top5_cache;
    """

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql)

        rows = await cur.fetchall()

        data = defaultdict(list)

        for row in rows:
            data[row["country_code"]].append(
                row
            )


        return data

@app.get("/api/news/{country_code}")
async def get_country(country_code: str, conn: AsyncConnection = Depends(get_conn)):
    country_code = _normalize_country_code(country_code)
    sql = """
        SELECT country_code, rank, url, headline,
        relevancy_score, country_name, source_name, themes, last_updated, is_cached
        FROM top5_cache
        WHERE country_code = (%s)
        ORDER BY rank;
    """

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql, (country_code,))
        rows = await cur.fetchall()
        
        return rows


@app.get("/api/scoring/defaults")
async def get_scoring_defaults():
    return {
        "weight_intensity": DEFAULT_WEIGHT_INTENSITY,
        "weight_richness": DEFAULT_WEIGHT_RICHNESS,
        "weight_locality": DEFAULT_WEIGHT_LOCALITY,
    }


@app.get("/api/relevancy/{country_code}")
async def preview_relevancy(
    country_code: str,
    weight_intensity: Optional[float] = Query(default=None, ge=0),
    weight_richness: Optional[float] = Query(default=None, ge=0),
    weight_locality: Optional[float] = Query(default=None, ge=0),
    conn: AsyncConnection = Depends(get_conn),
):
    return await _preview_scored_top5(
        conn,
        _normalize_country_code(country_code),
        weight_intensity=weight_intensity,
        weight_richness=weight_richness,
        weight_locality=weight_locality,
    )


@app.get("/api/locality/{country_code}")
async def get_locality(country_code: str, conn: AsyncConnection = Depends(get_conn)):
    country_code = _normalize_country_code(country_code)
    sql = """
        SELECT
            ca.country_code,
            COALESCE(cs.country_name, ca.country_code) AS country_name,
            COUNT(*)::INTEGER AS article_count,
            COALESCE(SUM(ca.total_source_location_count), 0)::INTEGER AS total_source_location_count,
            COALESCE(SUM(ca.total_location_count), 0)::INTEGER AS total_location_count,
            CASE
                WHEN COALESCE(SUM(ca.total_location_count), 0) = 0 THEN 0
                ELSE COALESCE(SUM(ca.total_source_location_count), 0)::double precision
                    / SUM(ca.total_location_count)
            END AS locality_ratio
        FROM country_articles ca
        LEFT JOIN country_status cs ON cs.country_code = ca.country_code
        WHERE ca.country_code = %s
        GROUP BY ca.country_code, cs.country_name;
    """

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql, (country_code,))
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"No locality data found for country code {country_code}.")

    return row


@app.post("/api/scoring/{country_code}")
async def update_scoring(
    country_code: str,
    weights: ScoringWeights,
    conn: AsyncConnection = Depends(get_conn),
):
    country_code = _normalize_country_code(country_code)
    resolved = _weights_response(
        weights.weight_intensity,
        weights.weight_richness,
        weights.weight_locality,
    )
    updated = await update_country_scoring_db(
        conn,
        country_code,
        weight_intensity=resolved["weight_intensity"],
        weight_richness=resolved["weight_richness"],
        weight_locality=resolved["weight_locality"],
    )

    return {
        "country_code": country_code,
        "updated": updated,
        "weights": resolved,
        "articles": await _get_top5_cache(conn, country_code),
    }
    
