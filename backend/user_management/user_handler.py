import uuid
from uuid import UUID

import bcrypt
from asyncpg import Connection

# help functions

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# async functions

async def create_user(user_connection:Connection,  userName: str, email: str, password: str, lastName: str, firstName: str) -> UUID:
        
    if not all([userName, email, password]):
        raise ValueError("Username, email, and password cannot be empty.")

    existing_user = await user_connection.fetchrow('SELECT * FROM users WHERE userName = $1 OR email = $2', userName, email)
    if existing_user:
        raise ValueError("Username or email already exists.")

    hashed_pw = hash_password(password)

    user_id = uuid.uuid4()

    await user_connection.execute(
        'INSERT INTO users (user_id, userName, email, password, lastName, firstName) VALUES ($1, $2, $3, $4, $5, $6)',
        user_id, userName, email, hashed_pw, lastName, firstName
    )
    return user_id

async def valid_password(user_connection:Connection, userKey: str, password: str) -> bool:

    if userKey is None or password is None:
        return False

    if "@" in userKey:
        user = await user_connection.fetchrow('SELECT * FROM users WHERE email = $1', userKey)
    else:
        user = await user_connection.fetchrow('SELECT * FROM users WHERE userName = $1', userKey)

    if user and verify_password(password, user['password']):
        return True
    return False

async def get_user_by_id(user_connection:Connection, user_id: int):
    user = await user_connection.fetchrow(
        'SELECT * FROM users WHERE user_id = $1',
        user_id
    )
    return user

async def get_user_by_username(user_connection:Connection, username: str):
    user = await user_connection.fetchrow(
        'SELECT * FROM users WHERE username = $1',
        username
    )
    return user

async def delete_user(user_connection:Connection, user_id: int):
    await user_connection.execute(
        'DELETE FROM users WHERE user_id = $1',
        user_id
    )

async def add_user_to_team(user_connection:Connection, user_id: int, team_id: int, role: str):
    await user_connection.execute(
        'INSERT INTO team_members (user_id, team_id, role) VALUES ($1, $2, $3)',
        user_id, team_id, role
    )

async def remove_user_from_team(user_connection:Connection, user_id: int, team_id: int):
    await user_connection.execute(
        'DELETE FROM team_members WHERE user_id = $1 AND team_id = $2',
        user_id, team_id
    )

