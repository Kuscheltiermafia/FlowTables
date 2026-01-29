"""
Tests for table cell operations (create, delete, get, set values).

These tests focus on table lifecycle and cell value management.
Separated from permission tests for better organization.
"""
import pytest
from uuid import UUID
from backend.data_management.table_handler import (
    create_table, delete_table, set_cell_value, get_cell_value
)


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_create_table(data_db_transaction, test_project):
    """Test creating a table in a project schema."""
    # Create a table using the test_project fixture
    table_name = "new_test_table"
    project_id = UUID(test_project) if isinstance(test_project, str) else test_project
    await create_table(data_db_transaction, table_name, project_id)
    
    # Verify table was created
    result = await data_db_transaction.fetch(
        '''SELECT tablename FROM pg_tables WHERE schemaname = $1 AND tablename = $2''',
        str(project_id), table_name
    )
    assert len(result) > 0, f"Table '{table_name}' should exist in schema '{project_id}'"
    assert result[0]['tablename'] == table_name, \
        f"Table name should be '{table_name}', got '{result[0]['tablename']}'"


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_create_table_duplicate(data_db_transaction, test_project):
    """Test creating a duplicate table raises error."""
    # Use test_project fixture
    project_id = UUID(test_project) if isinstance(test_project, str) else test_project
    
    # Create a table
    table_name = "duplicate_table"
    await create_table(data_db_transaction, table_name, project_id)
    
    # Try to create the same table again - should raise ValueError
    with pytest.raises(ValueError, match=f"Table {table_name} already exists in schema"):
        await create_table(data_db_transaction, table_name, project_id)


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_create_table_nonexistent_schema(data_db_transaction):
    """Test creating a table in non-existent schema raises error."""
    from uuid import uuid4
    fake_schema = uuid4()
    
    with pytest.raises(ValueError, match=f"Schema {str(fake_schema)} does not exist"):
        await create_table(data_db_transaction, "test_table", fake_schema)


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_delete_table(user_db_transaction, data_db_transaction, test_project):
    """Test deleting a table."""
    # Use test_project fixture
    project_id = UUID(test_project) if isinstance(test_project, str) else test_project
    
    # Create a table
    table_name = "delete_test_table"
    await create_table(data_db_transaction, table_name, project_id)
    
    # Delete the table (using project_id as table_id parameter)
    await delete_table(
        user_db_transaction, 
        data_db_transaction, 
        table_name, 
        project_id
    )
    
    # Verify table was deleted
    result = await data_db_transaction.fetch(
        '''SELECT tablename FROM pg_tables WHERE schemaname = $1 AND tablename = $2''',
        str(project_id), table_name
    )
    assert len(result) == 0, f"Table '{table_name}' should be deleted from schema '{project_id}'"


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_set_and_get_cell_value(data_db_transaction, test_table):
    """Test setting and getting cell values."""
    # Use test_table fixture
    table_name, project_id = test_table
    
    # Set a cell value
    test_value = "Test Value"
    await set_cell_value(data_db_transaction, project_id, table_name, 1, 1, test_value)
    
    # Get the cell value
    value = await get_cell_value(data_db_transaction, project_id, table_name, 1, 1)
    assert value == test_value, \
        f"Cell value should be '{test_value}', got '{value}'"


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_update_cell_value(data_db_transaction, test_table):
    """Test updating an existing cell value."""
    # Use test_table fixture
    table_name, project_id = test_table
    
    # Set initial value
    initial_value = "Initial Value"
    await set_cell_value(data_db_transaction, project_id, table_name, 2, 2, initial_value)
    value = await get_cell_value(data_db_transaction, project_id, table_name, 2, 2)
    assert value == initial_value, f"Initial value should be '{initial_value}', got '{value}'"
    
    # Update the value
    updated_value = "Updated Value"
    await set_cell_value(data_db_transaction, project_id, table_name, 2, 2, updated_value)
    value = await get_cell_value(data_db_transaction, project_id, table_name, 2, 2)
    assert value == updated_value, \
        f"Updated value should be '{updated_value}', got '{value}'"


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_delete_cell_value(data_db_transaction, test_table):
    """Test deleting a cell value by setting it to empty string."""
    # Use test_table fixture
    table_name, project_id = test_table
    
    # Set a value
    test_value = "Value to Delete"
    await set_cell_value(data_db_transaction, project_id, table_name, 3, 3, test_value)
    value = await get_cell_value(data_db_transaction, project_id, table_name, 3, 3)
    assert value == test_value, "Value should be set before deletion"
    
    # Delete the value by setting empty string
    await set_cell_value(data_db_transaction, project_id, table_name, 3, 3, "")
    value = await get_cell_value(data_db_transaction, project_id, table_name, 3, 3)
    assert value is None, "Cell value should be None after deletion"


@pytest.mark.table_operations
@pytest.mark.data_db
@pytest.mark.asyncio
async def test_get_nonexistent_cell_value(data_db_transaction, test_table):
    """Test getting a non-existent cell value returns None."""
    # Use test_table fixture
    table_name, project_id = test_table
    
    # Get a non-existent cell
    value = await get_cell_value(data_db_transaction, project_id, table_name, 99, 99)
    assert value is None, "Non-existent cell should return None"
