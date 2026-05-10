import pytest
import pytest_asyncio
import asyncio
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv
import os

load_dotenv()

TEST_DB_URL = f"postgresql://{os.getenv('USER')}:{os.getenv('PASS')}@localhost/worldwidenews_test"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def db_pool():
    pool = AsyncConnectionPool(conninfo=TEST_DB_URL, min_size=1, max_size=2, open=False)
    await pool.open()
    yield pool
    await pool.close()

@pytest_asyncio.fixture(scope="session")
async def setup_tables(db_pool):
    async with db_pool.connection() as conn:
        with open("schema.sql") as f:
            sql = f.read()
        async with conn.cursor() as cur:
            await cur.execute(sql)
        await conn.commit()

@pytest_asyncio.fixture
async def conn(db_pool, setup_tables):
    async with db_pool.connection() as c:
        yield c
        await c.rollback()
