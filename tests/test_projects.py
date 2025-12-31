import json

import pytest

from conftest import user_db_transaction
from backend.user_management.team_handler import create_team
from backend.data_management.project_handler import create_project, get_project_name, project_exists, add_member, \
    list_project_members, change_member_role, remove_member, delete_project, list_user_projects
from backend.user_management.user_handler import create_user


@pytest.mark.data_db
@pytest.mark.asyncio
async def test_setup_project(user_db_transaction, data_db_transaction):

    project_name = "Test Project"

    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="project_tester",
        email="project@tester.com",
        password="securepassword",
        lastName="Tester",
        firstName="Project"
    )

    team_id = await create_team(user_connection=user_db_transaction, team_name="Project Team")

    project_id = await create_project(user_connection=user_db_transaction, data_connection=data_db_transaction, project_name=project_name, owner_id=user_id)
    print(f"Created project with ID: {project_id}")
    db_project_name = await get_project_name(user_connection=user_db_transaction, project_id=project_id)
    assert db_project_name == project_name
    assert await project_exists(user_connection=user_db_transaction, project_id=project_id)

    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="project_member",
        email="other_user@mail.com",
        password="anotherpassword",
        lastName="Member",
        firstName="Project"
    )

    await add_member(user_connection=user_db_transaction, project_id=project_id, user_id=user2_id, role="editor")
    members = await list_project_members(user_connection=user_db_transaction, project_id=project_id)
    print(members)
    assert any(member['user_id'] == user2_id and json.loads(member['role']) == {"temp": "member"} for member in members)
    await change_member_role(user_connection=user_db_transaction, project_id=project_id, user_id=user2_id, new_role="moderator")
    members = await list_project_members(user_connection=user_db_transaction, project_id=project_id)
    assert any(member['user_id'] == user2_id and json.loads(member['role']) == {"temp": "moderator"} for member in members)

    await remove_member(user_connection=user_db_transaction, project_id=project_id, user_id=user2_id)
    members = await list_project_members(user_connection=user_db_transaction, project_id=project_id)
    assert all(member['user_id'] != user2_id for member in members)
    projects = await list_user_projects(user_connection=user_db_transaction, user_id=user2_id)
    assert all(project['project_id'] != project_id for project in projects)

    await delete_project(user_connection=user_db_transaction, data_connection=data_db_transaction, project_id=project_id)
    assert not await project_exists(user_connection=user_db_transaction, project_id=project_id)