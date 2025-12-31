from uuid import UUID

from asyncpg import Connection


async def create_table(data_connection: Connection, table_name: str, schema: str):
    existing_tables = await data_connection.fetch('''
        SELECT tablename FROM pg_tables WHERE schemaname = $1 AND tablename = $2
    ''', schema, table_name)
    if existing_tables:
        raise ValueError(f"Table {table_name} already exists in schema {schema}")

    existing_schema = await data_connection.fetch(f'''
        SELECT schema_name FROM information_schema.schemata WHERE schema_name = $1
    ''', schema)
    if not existing_schema:
        raise ValueError(f"Schema {schema} does not exist")

    await data_connection.execute(f'''CREATE TABLE "{schema}"."{table_name}" (
                                  row_index INT,
                                  col_index INT,
                                  value TEXT,
                                  PRIMARY KEY (row_index, col_index)
                                  )''')

async def delete_table(user_connection: Connection, data_connection: Connection, table_name: str, project_id: UUID):
    await data_connection.execute(f'''DROP TABLE IF EXISTS "{project_id}"."{table_name}" CASCADE''')
    await user_connection.execute(f'''DELETE FROM permissions."{project_id}" WHERE table_id = $1''', table_name)

async def set_cell_value(data_connection: Connection, schema: str, table_name: str, row: int, col: int, value: str):
    if not value:
        await data_connection.execute(f'''DELETE FROM "{schema}"."{table_name}" WHERE row_index = $1 AND col_index = $2''', row, col)
    else:
        await data_connection.execute(f'''
            INSERT INTO "{schema}"."{table_name}" (row_index, col_index, value)
            VALUES ($1, $2, $3)
            ON CONFLICT (row_index, col_index)
            DO UPDATE SET value = EXCLUDED.value
        ''', row, col, value)

async def get_cell_value(data_connection: Connection, schema: str, table_name: str, row: int, col: int) -> str | None:
    result = await data_connection.fetchrow(f'''
        SELECT value FROM "{schema}"."{table_name}" WHERE row_index = $1 AND col_index = $2
    ''', row, col)
    if result:
        return result['value']
    else:
        return None

async def set_permission(user_connection: Connection, project_id: UUID, table_id: UUID, user_id: UUID, start_row: int, end_row: int, start_col: int, end_col: int, permission: str):
    await user_connection.execute(f'''
        INSERT INTO permissions."{project_id}" (table_id, user_id, start_row, end_row, start_col, end_col, permission)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (table_id, user_id, start_row, end_row, start_col, end_col)
        DO UPDATE SET permission = EXCLUDED.permission
    ''', table_id, user_id, start_row, end_row, start_col, end_col, permission)

async def get_all_user_permissions(user_connection: Connection, project_id: UUID, table_id: UUID, user_id: UUID):
    permissions = await user_connection.fetch(f'''SELECT start_row, end_row, start_col, end_col, permission FROM permissions."{project_id}" where table_id = $1 AND user_id = $2''', table_id, user_id)
    return permissions

async def delete_all_user_permissions(user_connection: Connection, project_id: UUID, table_id: UUID, user_id: UUID):
    await user_connection.execute(f'''DELETE FROM permissions."{project_id}" WHERE table_id = $1 AND user_id = $2''', table_id, user_id)

async def delete_permission_range(user_connection: Connection, project_id: UUID, table_id: UUID, user_id: UUID, start_row: int, end_row: int, start_col: int, end_col: int):
    await user_connection.execute(f'''DELETE FROM permissions."{project_id}" WHERE table_id = $1 AND user_id = $2 AND start_row = $3 AND end_row = $4 AND start_col = $5 AND end_col = $6''', table_id, user_id, start_row, end_row, start_col, end_col)