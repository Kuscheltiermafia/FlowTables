import json
from uuid import UUID

from asyncpg import Connection
import uuid

from pydantic import Json


async def create_project(user_connection:Connection, data_connection:Connection, project_name: str, owner_id: UUID):
    project_id = uuid.uuid4()

    await data_connection.execute(f'CREATE SCHEMA "{project_id}"')
    await user_connection.execute('INSERT INTO projects (project_id, project_name, owner_id) VALUES ($1, $2, $3)', project_id, project_name, owner_id)
    await user_connection.execute('INSERT INTO project_members (project_id, user_id, role) VALUES ($1, $2, $3)', project_id, owner_id, 'owner')

    await user_connection.execute(f'''CREATE TABLE IF NOT EXISTS permissions."{project_id}" (
        table_id UUID,
        user_id UUID REFERENCES users ("user_id") ON DELETE CASCADE,
        start_row INT NOT NULL,
        end_row INT NOT NULL,
        start_col INT NOT NULL,
        end_col INT NOT NULL,
        permission table_permission NOT NULL DEFAULT 'none',
        PRIMARY KEY (table_id, user_id, start_row, end_row, start_col, end_col),
        CONSTRAINT valid_row_range CHECK (end_row >= start_row),
        CONSTRAINT valid_col_range CHECK (end_col >= start_col)
    )''')

    return str(project_id)


async def get_project_name(user_connection:Connection, project_id: UUID) -> str | None:

    result = await user_connection.fetchrow('SELECT project_name FROM projects WHERE project_id = $1', project_id)
    if result:
        return result['project_name']
    else:
        return None

async def delete_project(user_connection:Connection, data_connection:Connection, project_id: UUID):
    await data_connection.execute(f'DROP SCHEMA IF EXISTS "{project_id}" CASCADE')
    await user_connection.execute(f'DROP TABLE IF EXISTS permissions."{project_id}" CASCADE')
    await user_connection.execute('DELETE FROM projects WHERE project_id = $1', project_id)
    await user_connection.execute('DELETE FROM project_members WHERE project_id = $1', project_id)
    await user_connection.execute('DELETE FROM project_teams WHERE project_id = $1', project_id)

async def project_exists(user_connection:Connection, project_id: UUID) -> bool:
    result = await user_connection.fetchrow('SELECT 1 FROM projects WHERE project_id = $1', project_id)
    return result is not None

async def add_member(user_connection:Connection, project_id: UUID, user_id: UUID, role: str):
    await user_connection.execute('INSERT INTO project_members (project_id, user_id, role) VALUES ($1, $2, $3)', project_id, user_id, role)

async def remove_member(user_connection:Connection, project_id: UUID, user_id: UUID):
    await user_connection.execute('DELETE FROM project_members WHERE project_id = $1 AND user_id = $2', project_id, user_id)

async def list_project_members(user_connection:Connection, project_id: UUID):
    results = await user_connection.fetch('SELECT user_id, role FROM project_members WHERE project_id = $1', project_id)
    return [{'user_id': record['user_id'], 'role': record['role']} for record in results]

async def change_member_role(user_connection:Connection, project_id: UUID, user_id: UUID, new_role: str):
    await user_connection.execute('UPDATE project_members SET role = $1 WHERE project_id = $2 AND user_id = $3', new_role, project_id, user_id)

async def list_user_projects(user_connection:Connection, user_id: UUID):
    results = await user_connection.fetch('SELECT project_id, project_name, role FROM projects JOIN project_members USING (project_id) WHERE user_id = $1', user_id)
    return [{'project_id': record['project_id'], 'project_name': record['project_name'], 'role': record['role']} for record in results]
