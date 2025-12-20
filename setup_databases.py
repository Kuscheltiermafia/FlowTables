import os

import asyncpg
import asyncio

from dotenv import load_dotenv


async def setup_databases():
    #Load environment variables from .env.deployment file if not in CI environment
    if os.getenv('CI') is None:
        print("Loading environment variables from .env.deployment")
        load_dotenv('.env.deployment')

    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')

    user_db_name = os.getenv('USER_DB_NAME')
    data_db_name = os.getenv('DATA_DB_NAME')

    print(f"Host: {host}, Port: {port}, User DB: {user_db_name}, Data DB: {data_db_name}")

    #Connect to the PostgreSQL server
    print("Connecting to PostgreSQL server with authentication")
    setup_db_conn = await asyncpg.connect(host=host, port=port, user=user, password=password)

    #Create 'users' database
    exists = await setup_db_conn.fetchval(
        'SELECT 1 FROM pg_database WHERE datname = $1', user_db_name
    )
    print(f"Database '{user_db_name}' exists: {bool(exists)}")
    if not exists:
        print(f"Creating database '{user_db_name}'")
        await setup_db_conn.execute(f'CREATE DATABASE "{user_db_name}"')

    #Create 'data' database
    exists = await setup_db_conn.fetchval(
        'SELECT 1 FROM pg_database WHERE datname = $1', data_db_name
    )
    print(f"Database '{data_db_name}' exists: {bool(exists)}")
    if not exists:
        print(f"Creating database '{data_db_name}'")
        await setup_db_conn.execute(f'CREATE DATABASE "{data_db_name}"')

    #Close connection to the PostgreSQL server
    await setup_db_conn.close()

    await asyncio.sleep(1)  #Wait a moment to ensure the database is created before connecting

    #Connect to the 'users' database

    print("Connecting to 'users' database with authentication")
    conn = await asyncpg.connect(host=host, port=port, database=user_db_name, user=user, password=password)

    #Create 'users' table
    await conn.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id    SERIAL NOT NULL PRIMARY KEY,
        username  VARCHAR(25) NOT NULL UNIQUE,
        email     VARCHAR(50) NOT NULL,
        password  VARCHAR(100) NOT NULL UNIQUE,
        lastname VARCHAR(50),
        firstname VARCHAR(50)
        )''')
    print("Created 'users' table in 'users' database")

    #Create 'teams' table
    await conn.execute('''CREATE TABLE IF NOT EXISTS teams (
        team_id SERIAL PRIMARY KEY,
        team_name VARCHAR(50) NOT NULL UNIQUE
        )''')
    print("Created 'teams' table in 'users' database")

    # Creating 'team_role'
    await conn.execute('''
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'team_role') THEN
                            CREATE TYPE team_role AS ENUM ('member', 'moderator', 'admin', 'owner');
                        END IF;
                    END$$;
                ''')
    print("Created 'team_role' enum type in 'users' database")

    # Create 'team_members' table
    #Etvl. Perms weiter ausarbeiten / ändern
    await conn.execute('''CREATE TABLE IF NOT EXISTS team_members(
        user_id INT REFERENCES users ("user_id") ON DELETE CASCADE,
        team_id INT REFERENCES teams ("team_id") ON DELETE CASCADE,
        role team_role NOT NULL DEFAULT 'member',
        PRIMARY KEY (user_id, team_id)
        )''')
    print("Created 'team_members' table in 'users' database")

    #Create 'projects' table
    await conn.execute('''CREATE TABLE IF NOT EXISTS projects (
        project_id VARCHAR(36) PRIMARY KEY,
        project_name VARCHAR(50) NOT NULL,
        owner_id INT REFERENCES users ("user_id") ON DELETE SET NULL
        )''')
    print("Created 'projects' table in 'users' database")

    #Create 'project_members' table
    await conn.execute('''CREATE TABLE IF NOT EXISTS project_members (
        user_id INT REFERENCES users ("user_id") ON DELETE CASCADE,
        project_id VARCHAR(36) REFERENCES projects ("project_id") ON DELETE CASCADE,
        permission json
        )''')
    print("Created 'project_members' table in 'users' database")

    #Create 'project_teams' table
    await conn.execute('''CREATE TABLE IF NOT EXISTS project_teams (
        team_id INT REFERENCES teams ("team_id") ON DELETE CASCADE,
        project_id VARCHAR(36) REFERENCES projects ("project_id") ON DELETE CASCADE,
        permission json
        )''')
    print("Created 'project_teams' table in 'users' database")

    #Close the connection to the 'users' database
    await conn.close()

if __name__ == '__main__':
    asyncio.run(setup_databases())