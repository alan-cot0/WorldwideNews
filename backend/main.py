import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pipeline import run_pipeline
from scorer import load_cache, CACHE_PATH


# Run pipeline on startup if no cache exists, then every 12 hours
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_pipeline, "interval", hours=12)
    scheduler.start()

    if not os.path.exists(CACHE_PATH):
        run_pipeline()

    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# Returns top 5 articles for a given 2-letter country code
@app.get("/api/news/{country_code}")
async def get_news(country_code: str):
    try:
        cache = load_cache()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Pipeline has not run yet")

    articles = cache.get(country_code.upper())
    if not articles:
        raise HTTPException(status_code=404, detail="No data for this country")

    return {"country_code": country_code.upper(), "articles": articles}


# Returns all country codes that have data in the cache
@app.get("/api/countries")
async def get_countries():
    try:
        cache = load_cache()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Pipeline has not run yet")

    return {
        "countries": [
            {"country_code": code, "article_count": len(articles)}
            for code, articles in cache.items()
        ]
    }
