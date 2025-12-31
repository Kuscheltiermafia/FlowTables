import pytest
from uuid import uuid4, UUID
from backend.data_management.table_handler import (
    create_table, delete_table, set_cell_value, get_cell_value,
    set_permission, get_all_user_permissions, delete_all_user_permissions,
    delete_permission_range
)
from backend.data_management.project_handler import create_project, delete_project
from backend.user_management.user_handler import create_user


@pytest.mark.data_db
@pytest.mark.asyncio
async def test_create_table(user_db_transaction, data_db_transaction):
    """Test creating a table in a project schema."""
    # Create a test user and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="table_test_user",
        email="table@test.com",
        password="SecurePass123!",
        lastName="Table",
        firstName="Test"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Table Test Project",
        owner_id=user_id
    )
    
    # Create a table
    table_name = "test_table"
    await create_table(data_db_transaction, table_name, str(project_id))
    
    # Verify table was created
    result = await data_db_transaction.fetch(
        '''SELECT tablename FROM pg_tables WHERE schemaname = $1 AND tablename = $2''',
        str(project_id), table_name
    )
    assert len(result) > 0
    assert result[0]['tablename'] == table_name


@pytest.mark.asyncio
@pytest.mark.data_db
async def test_create_table_duplicate(user_db_transaction, data_db_transaction):
    """Test creating a duplicate table raises error."""
    # Create a test user and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="duplicate_table_user",
        email="dup_table@test.com",
        password="SecurePass123!",
        lastName="DupTable",
        firstName="Test"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Duplicate Table Test",
        owner_id=user_id
    )
    
    # Create a table
    table_name = "duplicate_table"
    await create_table(data_db_transaction, table_name, str(project_id))
    
    # Try to create the same table again
    with pytest.raises(ValueError, match=f"Table {table_name} already exists in schema"):
        await create_table(data_db_transaction, table_name, str(project_id))


@pytest.mark.asyncio
@pytest.mark.data_db
async def test_create_table_nonexistent_schema(data_db_transaction):
    """Test creating a table in non-existent schema raises error."""
    fake_schema = str(uuid4())
    with pytest.raises(ValueError, match=f"Schema {fake_schema} does not exist"):
        await create_table(data_db_transaction, "test_table", fake_schema)


@pytest.mark.asyncio
@pytest.mark.data_db
async def test_delete_table(user_db_transaction, data_db_transaction):
    """Test deleting a table."""
    # Create a test user and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="delete_table_user",
        email="del_table@test.com",
        password="SecurePass123!",
        lastName="DelTable",
        firstName="Test"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Delete Table Test",
        owner_id=user_id
    )
    
    # Create a table
    table_name = "delete_test_table"
    await create_table(data_db_transaction, table_name, str(project_id))
    
    # Delete the table (using project_id as table_id parameter)
    await delete_table(user_db_transaction, data_db_transaction, table_name, UUID(project_id) if isinstance(project_id, str) else project_id)
    
    # Verify table was deleted
    result = await data_db_transaction.fetch(
        '''SELECT tablename FROM pg_tables WHERE schemaname = $1 AND tablename = $2''',
        str(project_id), table_name
    )
    assert len(result) == 0


@pytest.mark.asyncio
@pytest.mark.data_db
async def test_set_and_get_cell_value(user_db_transaction, data_db_transaction):
    """Test setting and getting cell values."""
    # Create a test user and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="cell_test_user",
        email="cell@test.com",
        password="SecurePass123!",
        lastName="Cell",
        firstName="Test"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Cell Test Project",
        owner_id=user_id
    )
    
    # Create a table
    table_name = "cell_test_table"
    await create_table(data_db_transaction, table_name, str(project_id))
    
    # Set a cell value
    await set_cell_value(data_db_transaction, str(project_id), table_name, 1, 1, "Test Value")
    
    # Get the cell value
    value = await get_cell_value(data_db_transaction, str(project_id), table_name, 1, 1)
    assert value == "Test Value"


@pytest.mark.asyncio
@pytest.mark.data_db
async def test_update_cell_value(user_db_transaction, data_db_transaction):
    """Test updating an existing cell value."""
    # Create a test user and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="update_cell_user",
        email="update_cell@test.com",
        password="SecurePass123!",
        lastName="UpdateCell",
        firstName="Test"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Update Cell Test",
        owner_id=user_id
    )
    
    # Create a table
    table_name = "update_cell_table"
    await create_table(data_db_transaction, table_name, str(project_id))
    
    # Set initial value
    await set_cell_value(data_db_transaction, str(project_id), table_name, 2, 2, "Initial Value")
    value = await get_cell_value(data_db_transaction, str(project_id), table_name, 2, 2)
    assert value == "Initial Value"
    
    # Update the value
    await set_cell_value(data_db_transaction, str(project_id), table_name, 2, 2, "Updated Value")
    value = await get_cell_value(data_db_transaction, str(project_id), table_name, 2, 2)
    assert value == "Updated Value"


@pytest.mark.asyncio
@pytest.mark.data_db
async def test_delete_cell_value(user_db_transaction, data_db_transaction):
    """Test deleting a cell value by setting it to empty string."""
    # Create a test user and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="delete_cell_user",
        email="delete_cell@test.com",
        password="SecurePass123!",
        lastName="DeleteCell",
        firstName="Test"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="Delete Cell Test",
        owner_id=user_id
    )
    
    # Create a table
    table_name = "delete_cell_table"
    await create_table(data_db_transaction, table_name, str(project_id))
    
    # Set a value
    await set_cell_value(data_db_transaction, str(project_id), table_name, 3, 3, "Value to Delete")
    value = await get_cell_value(data_db_transaction, str(project_id), table_name, 3, 3)
    assert value == "Value to Delete"
    
    # Delete the value by setting empty string
    await set_cell_value(data_db_transaction, str(project_id), table_name, 3, 3, "")
    value = await get_cell_value(data_db_transaction, str(project_id), table_name, 3, 3)
    assert value is None


@pytest.mark.asyncio
@pytest.mark.data_db
async def test_get_nonexistent_cell_value(user_db_transaction, data_db_transaction):
    """Test getting a non-existent cell value returns None."""
    # Create a test user and project
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="nonexist_cell_user",
        email="nonexist_cell@test.com",
        password="SecurePass123!",
        lastName="NonExist",
        firstName="Cell"
    )
    
    project_id = await create_project(
        user_connection=user_db_transaction,
        data_connection=data_db_transaction,
        project_name="NonExist Cell Test",
        owner_id=user_id
    )
    
    # Create a table
    table_name = "nonexist_cell_table"
    await create_table(data_db_transaction, table_name, str(project_id))
    
    # Get a non-existent cell
    value = await get_cell_value(data_db_transaction, str(project_id), table_name, 99, 99)
    assert value is None


@pytest.mark.asyncio
@pytest.mark.data_db
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
    assert len(perms) > 0
    assert any(p['permission'] == "read" for p in perms)


@pytest.mark.asyncio
@pytest.mark.data_db
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
    assert len(perms) > 0
    assert any(p['permission'] == "write" for p in perms)


@pytest.mark.asyncio
@pytest.mark.data_db
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
    
    assert len(perms) >= 2
    assert any(p['permission'] == "read" for p in perms)
    assert any(p['permission'] == "write" for p in perms)


@pytest.mark.asyncio
@pytest.mark.data_db
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
    assert len(perms) > 0
    
    # Delete all permissions
    await delete_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    
    # Verify all permissions are deleted
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    assert len(perms) == 0


@pytest.mark.asyncio
@pytest.mark.data_db
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
    assert initial_count >= 2
    
    # Delete specific range
    await delete_permission_range(user_db_transaction, proj_uuid, table_id, user2_id, 0, 5, 0, 5)
    
    # Verify only the specified permission is deleted
    perms = await get_all_user_permissions(user_db_transaction, proj_uuid, table_id, user2_id)
    assert len(perms) == initial_count - 1
    assert not any(p['start_row'] == 0 and p['end_row'] == 5 for p in perms)
