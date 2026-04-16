from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from utils.parse_csv import clear_tables, create_tables, load_mappings, refresh_15min
from dotenv import load_dotenv
import os
from collections import defaultdict
from dataclasses import dataclass, asdict


from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg.rows import dict_row

load_dotenv()

DB_URL = "postgresql://localhost/worldwidenews"

# To not request too much from GDELT
USE_CACHE = False

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
         

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await pool.open()
    
    async with pool.connection() as conn:
        #await clear_tables(conn)
        await create_tables(conn)
        await load_mappings(conn)
        await refresh_15min(conn, USE_CACHE)
        
    yield

    await pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}



# Will be useful in future
@dataclass
class Article:
    domain: str
    url: str

# Not finalized, just something for
# the frontend to play around with

@app.get("/api/countries")
async def get_countries(conn: AsyncConnection = Depends(get_conn)):
    sql = """
        SELECT CA.url, CA.source_name, CA.country_code
        FROM country_articles CA, country_mappings CM
        WHERE CA.source_name = CM.domain_name;
    """

    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql)

        rows = await cur.fetchall()

        data = defaultdict(list)

        for row in rows:
            data[row["country_code"]].append(
                asdict(Article(row["source_name"], row["url"]))
            )


        return data
