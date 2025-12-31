import asyncpg
from dotenv import load_dotenv
import os

# noinspection PyTypeChecker
data_pool : asyncpg.Pool = None

async def init_data_pool():

    print("Initializing data database pool...")

    load_dotenv('.env.deployment')
    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT')
    database = os.getenv('DATA_DB_NAME')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')

    global data_pool
    # noinspection PyUnresolvedReferences
    data_pool = await asyncpg.create_pool(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
    )

    print("Data database pool initialized.")

async def close_data_pool():
    global data_pool
    if data_pool is not None:
        await data_pool.close()
        data_pool = None

        print("Data database pool closed.")

async def get_data_pool():
    with data_pool.acquire() as conn:
        yield conn