import asyncio
import os
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
from utils.scorer import populate_top5_all_countries

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

DB_URL = f"postgresql://{os.getenv('USER')}:{os.getenv('PASS')}@localhost/worldwidenews"

async def main():
    pool = AsyncConnectionPool(
        conninfo=DB_URL,
        min_size=1,
        max_size=4,
        open=False
    )

    await pool.open()

    async with pool.connection() as conn:
        await populate_top5_all_countries(conn)

    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())