import uuid
from uuid import UUID

import asyncpg
from asyncpg import Connection

async def create_team(user_connection:Connection, team_name: str) -> UUID:

    team_id = uuid.uuid4()
    await user_connection.execute(
        'INSERT INTO teams (team__id, team_name) VALUES ($1, $2)',
        team_id, team_name
    )
    return team_id

async def get_team_by_id(user_connection:Connection, team_id: int):

    team = await user_connection.fetchrow(
        'SELECT * FROM teams WHERE team_id = $1',
        team_id
    )
    return team

async def get_team_by_name(user_connection:Connection, team_name: str):

    team = await user_connection.fetchrow(
        'SELECT * FROM teams WHERE team_name = $1',
        team_name
    )
    return team

async def delete_team(user_connection:Connection, team_id: int):

    await user_connection.execute(
        'DELETE FROM teams WHERE team_id = $1',
        team_id
    )