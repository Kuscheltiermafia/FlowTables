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
from backend.data_management.project_handler import create_project
from backend.user_management.user_handler import create_user


@pytest.mark.table_permissions
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_set_permission(user_db_transaction, data_db_transaction):
    """Test setting permissions for a user on a table."""
    # Create test users and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="perm_owner_user",
        email="perm_owner@test.com",
        password="SecurePass123!",
        lastName="PermOwner",
        firstName="Test"
    )
    
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="perm_user",
        email="perm@test.com",
        password="SecurePass123!",
        lastName="Perm",
        firstName="User"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Permission Test Project",
        owner_id=user_id
    )
    
    table_id = uuid4()
    
    # Set permission
    await set_permission(
        user_db_transaction, UUID(project_id) if isinstance(project_id, str) else project_id,
        table_id, user2_id, 0, 10, 0, 10, "read"
    )
    
    # Verify permission was set
    perms = await get_all_user_permissions(
        user_db_transaction, UUID(project_id) if isinstance(project_id, str) else project_id,
        table_id, user2_id
    )
    assert len(perms) > 0, f"User {user2_id} should have at least one permission"
    assert any(p['permission'] == "read" for p in perms), \
        "User should have 'read' permission"


@pytest.mark.table_permissions
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_update_permission(user_db_transaction, data_db_transaction):
    """Test updating an existing permission."""
    # Create test users and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="update_perm_owner",
        email="update_perm_owner@test.com",
        password="SecurePass123!",
        lastName="UpdatePermOwner",
        firstName="Test"
    )
    
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="update_perm_user",
        email="update_perm@test.com",
        password="SecurePass123!",
        lastName="UpdatePerm",
        firstName="User"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Update Perm Test",
        owner_id=user_id
    )
    
    table_id = uuid4()
    proj_uuid = UUID(project_id) if isinstance(project_id, str) else project_id
    
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
async def test_get_all_user_permissions(user_db_transaction, data_db_transaction):
    """Test getting all permissions for a user."""
    # Create test users and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="get_perm_owner",
        email="get_perm_owner@test.com",
        password="SecurePass123!",
        lastName="GetPermOwner",
        firstName="Test"
    )
    
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="get_perm_user",
        email="get_perm@test.com",
        password="SecurePass123!",
        lastName="GetPerm",
        firstName="User"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Get Perm Test",
        owner_id=user_id
    )
    
    table_id = uuid4()
    proj_uuid = UUID(project_id) if isinstance(project_id, str) else project_id
    
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
async def test_delete_all_user_permissions(user_db_transaction, data_db_transaction):
    """Test deleting all permissions for a user."""
    # Create test users and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="del_all_perm_owner",
        email="del_all_perm_owner@test.com",
        password="SecurePass123!",
        lastName="DelAllPermOwner",
        firstName="Test"
    )
    
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="del_all_perm_user",
        email="del_all_perm@test.com",
        password="SecurePass123!",
        lastName="DelAllPerm",
        firstName="User"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Del All Perm Test",
        owner_id=user_id
    )
    
    table_id = uuid4()
    proj_uuid = UUID(project_id) if isinstance(project_id, str) else project_id
    
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
async def test_delete_permission_range(user_db_transaction, data_db_transaction):
    """Test deleting a specific permission range."""
    # Create test users and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="del_range_perm_owner",
        email="del_range_perm_owner@test.com",
        password="SecurePass123!",
        lastName="DelRangePermOwner",
        firstName="Test"
    )
    
    user2_id = await create_user(
        user_connection=user_db_transaction,
        userName="del_range_perm_user",
        email="del_range_perm@test.com",
        password="SecurePass123!",
        lastName="DelRangePerm",
        firstName="User"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Del Range Perm Test",
        owner_id=user_id
    )
    
    table_id = uuid4()
    proj_uuid = UUID(project_id) if isinstance(project_id, str) else project_id
    
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
