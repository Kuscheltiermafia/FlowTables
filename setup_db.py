
import asyncio
import asyncpg
from app.core.config import settings

# --- SQL Statements for table creation in user_db ---

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    userName VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    lastName VARCHAR(50),
    firstName VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

TEAMS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    owner_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

TEAM_MEMBERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS team_members (
    team_id INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    PRIMARY KEY (team_id, user_id)
);
"""

PROJECTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(36) PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    owner_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""


async def create_databases_and_tables():
    """Connects to PostgreSQL, creates databases if they don't exist, and then creates tables."""
    # Connect to the default 'postgres' database to create other databases
    try:
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )
        print("Successfully connected to PostgreSQL server.")
    except Exception as e:
        print(f"Could not connect to PostgreSQL server: {e}")
        return

    # Create databases
    for db_name in [settings.USER_DB_NAME, settings.DATA_DB_NAME]:
        try:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully.")
        except asyncpg.DuplicateDatabaseError:
            print(f"Database '{db_name}' already exists.")
        except Exception as e:
            print(f"Error creating database '{db_name}': {e}")
    await conn.close()

    # --- Connect to user_db and create tables ---
    try:
        conn = await asyncpg.connect(dsn=settings.USER_DB_URL)
        print(f"Successfully connected to '{settings.USER_DB_NAME}' database.")
        
        print("Creating tables in user_db...")
        await conn.execute(USERS_TABLE_SQL)
        await conn.execute(TEAMS_TABLE_SQL)
        await conn.execute(TEAM_MEMBERS_TABLE_SQL)
        await conn.execute(PROJECTS_TABLE_SQL)
        print("Tables in user_db created successfully (if they didn't exist).")
        
        await conn.close()
    except Exception as e:
        print(f"Error connecting to '{settings.USER_DB_NAME}' or creating tables: {e}")

    print("\nDatabase setup process finished.")

if __name__ == "__main__":
    print("Starting database setup...")
    asyncio.run(create_databases_and_tables())
