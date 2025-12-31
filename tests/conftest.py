import pytest
import asyncpg
import os

import pytest_asyncio
from dotenv import load_dotenv


@pytest_asyncio.fixture
async def data_db_pool():

    if os.getenv('CI') is None:
        load_dotenv('.env.deployment')

    # noinspection PyUnresolvedReferences
    pool = await asyncpg.create_pool(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('DATA_DB_NAME'),
    )

    yield pool

    await pool.close()

@pytest_asyncio.fixture
async def data_db_transaction(data_db_pool):
    async with data_db_pool.acquire() as connection:
        transaction = connection.transaction()
        await transaction.start()
        try:
            yield connection
        finally:
            await transaction.rollback()



@pytest_asyncio.fixture
async def user_db_pool():
    if os.getenv('CI') is None:
        load_dotenv('.env.deployment')

    # noinspection PyUnresolvedReferences
    pool = await asyncpg.create_pool(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('USER_DB_NAME'),
    )

    yield pool

    await pool.close()

@pytest_asyncio.fixture
async def user_db_transaction(user_db_pool):
    async with user_db_pool.acquire() as connection:
        transaction = connection.transaction()
        await transaction.start()
        try:
            yield connection
        finally:
            await transaction.rollback()


# Helper fixtures for common test setup
@pytest_asyncio.fixture
async def test_user(user_db_transaction):
    """Create a test user for use in tests."""
    from backend.user_management.user_handler import create_user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="test_user",
        email="test@example.com",
        password="TestPassword123!",
        lastName="User",
        firstName="Test"
    )
    return user_id


@pytest_asyncio.fixture
async def test_project(user_db_transaction, data_db_transaction, test_user):
    """Create a test project for use in tests."""
    from backend.data_management.project_handler import create_project
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Test Project",
        owner_id=test_user
    )
    return project_id


@pytest_asyncio.fixture
async def test_table(data_db_transaction, test_project):
    """Create a test table in a test project."""
    from backend.data_management.table_handler import create_table
    table_name = "test_table"
    await create_table(data_db_transaction, table_name, str(test_project))
    return table_name, test_project