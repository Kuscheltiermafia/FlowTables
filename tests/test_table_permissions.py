"""
Tests for table permission management.

These tests focus on setting, getting, and deleting permissions for users on tables.
Separated from table operations tests for better organization.
"""
import pytest
from uuid import uuid4, UUID
from backend.data_management.table_handler import (
    set_permission, get_all_user_permissions, delete_all_user_permissions,
    delete_permission_range
)
from backend.user_management.user_handler import create_user


@pytest.mark.table_permissions
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_set_permission(user_db_transaction, data_db_transaction, test_user, test_project):
    """Test setting permissions for a user on a table."""
    # Use test_user from fixture, create a second user
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="perm_user",
        email="perm@test.com",
        password="SecurePass123!",
        lastName="Perm",
        firstName="User"
    )
    
    # Use test_project from fixture
    project_id = UUID(test_project) if isinstance(test_project, str) else test_project
    table_id = uuid4()
    
    # Set permission
    await set_permission(
        user_db_transaction, project_id,
        table_id, user2_id, 0, 10, 0, 10, "read"
    )
    
    # Verify permission was set
    perms = await get_all_user_permissions(
        user_db_transaction, project_id,
        table_id, user2_id
    )
    assert len(perms) > 0, f"User {user2_id} should have at least one permission"
    assert any(p['permission'] == "read" for p in perms), \
        "User should have 'read' permission"


@pytest.mark.table_permissions
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_update_permission(user_db_transaction, data_db_transaction, test_user, test_project):
    """Test updating an existing permission."""
    # Use test_user from fixture, create a second user
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="update_perm_user",
        email="update_perm@test.com",
        password="SecurePass123!",
        lastName="UpdatePerm",
        firstName="User"
    )
    
    # Use test_project from fixture
    proj_uuid = UUID(test_project) if isinstance(test_project, str) else test_project
    table_id = uuid4()
    
    # Set initial permission
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 0, 10, 0, 10, "read")
    
    # Update permission
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 0, 10, 0, 10, "write")
    
    # Verify permission was updated
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    assert len(perms) > 0, "User should have at least one permission"
    assert any(p['permission'] == "write" for p in perms), \
        "Permission should be updated to 'write'"


@pytest.mark.table_permissions
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_get_all_user_permissions(user_db_transaction, data_db_transaction, test_user, test_project):
    """Test getting all permissions for a user."""
    # Use test_user from fixture, create a second user
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="get_perm_user",
        email="get_perm@test.com",
        password="SecurePass123!",
        lastName="GetPerm",
        firstName="User"
    )
    
    # Use test_project from fixture
    proj_uuid = UUID(test_project) if isinstance(test_project, str) else test_project
    table_id = uuid4()
    
    # Set multiple permissions
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 0, 5, 0, 5, "read")
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 6, 10, 6, 10, "write")
    
    # Get all permissions
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    
    assert len(perms) >= 2, f"User should have at least 2 permissions, got {len(perms)}"
    assert any(p['permission'] == "read" for p in perms), \
        "User should have 'read' permission"
    assert any(p['permission'] == "write" for p in perms), \
        "User should have 'write' permission"


@pytest.mark.table_permissions
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_delete_all_user_permissions(user_db_transaction, data_db_transaction, test_user, test_project):
    """Test deleting all permissions for a user."""
    # Use test_user from fixture, create a second user
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="del_all_perm_user",
        email="del_all_perm@test.com",
        password="SecurePass123!",
        lastName="DelAllPerm",
        firstName="User"
    )
    
    # Use test_project from fixture
    proj_uuid = UUID(test_project) if isinstance(test_project, str) else test_project
    table_id = uuid4()
    
    # Set permissions
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 0, 5, 0, 5, "read")
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 6, 10, 6, 10, "write")
    
    # Verify permissions exist
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    assert len(perms) > 0, "User should have permissions before deletion"
    
    # Delete all permissions
    await delete_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    
    # Verify all permissions are deleted
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    assert len(perms) == 0, f"All permissions should be deleted, found {len(perms)}"


@pytest.mark.table_permissions
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_delete_permission_range(user_db_transaction, data_db_transaction, test_user, test_project):
    """Test deleting a specific permission range."""
    # Use test_user from fixture, create a second user
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="del_range_perm_user",
        email="del_range_perm@test.com",
        password="SecurePass123!",
        lastName="DelRangePerm",
        firstName="User"
    )
    
    # Use test_project from fixture
    proj_uuid = UUID(test_project) if isinstance(test_project, str) else test_project
    table_id = uuid4()
    
    # Set multiple permissions
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 0, 5, 0, 5, "read")
    await set_permission(user_db_transaction, proj_uuid, table_id, user2_id, 6, 10, 6, 10, "write")
    
    # Verify both permissions exist
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    initial_count = len(perms)
    assert initial_count >= 2, f"User should have at least 2 permissions, got {initial_count}"
    
    # Delete specific range
    await delete_permission_range(user_db_transaction, proj_uuid, table_id, user2_id, 0, 5, 0, 5)
    
    # Verify only the specified permission is deleted
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    assert len(perms) == initial_count - 1, \
        f"One permission should be deleted, expected {initial_count - 1}, got {len(perms)}"
    assert not any(p['start_row'] == 0 and p['end_row'] == 5 for p in perms), \
        "Permission range (0-5, 0-5) should be deleted"
