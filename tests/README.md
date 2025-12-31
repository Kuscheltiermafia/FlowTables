# Test Organization

This directory contains comprehensive tests for the FlowTables backend and web application.

## Test Files

### User Management Tests
- **test_user_handler.py** - Tests for user operations (create, get, delete, password validation, team membership)
- **test_team_handler.py** - Tests for team operations (create, get by ID/name, delete)
- **test_user_creation.py** - Basic user creation test

### Project Management Tests
- **test_projects.py** - Tests for project management (create, delete, members, roles)

### Table Management Tests
- **test_table_operations.py** - Tests for table lifecycle and cell operations
  - Table creation and deletion
  - Cell value operations (set, get, update, delete)
  - Schema validation
- **test_table_permissions.py** - Tests for permission management
  - Setting and updating permissions
  - Getting user permissions
  - Deleting permissions (all or by range)
- **test_table_handler.py** - Original comprehensive table tests (will be deprecated)

### Web/UI Tests
- **test_web_routes.py** - Tests for web application routes and pages
  - Index/homepage
  - Login/logout functionality
  - Dashboard access control
  - Error pages (403, 404, 500)
  - Static file serving
  - Session middleware
  - Custom headers and middleware

### API Tests
- **test_api.py** - API endpoint tests

## Test Markers

Tests are organized with pytest markers for selective test execution:

- `@pytest.mark.user_creation` - User and team management tests
- `@pytest.mark.data_db` - Tests requiring data database
- `@pytest.mark.table_operations` - Table and cell operation tests
- `@pytest.mark.table_permissions` - Permission management tests
- `@pytest.mark.web` - Web route and UI tests

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific marker groups
```bash
# User management tests
pytest -m user_creation

# Data database tests
pytest -m data_db

# Table operation tests only
pytest -m table_operations

# Permission tests only
pytest -m table_permissions

# Web/UI tests only
pytest -m web
```

### Run specific test files
```bash
pytest tests/test_user_handler.py
pytest tests/test_table_operations.py
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `user_db_transaction` - User database connection with transaction rollback
- `data_db_transaction` - Data database connection with transaction rollback
- `test_user` - Creates a test user for use in tests
- `test_project` - Creates a test project with a test user
- `test_table` - Creates a test table in a test project

## Writing Tests

### Best Practices

1. **Use descriptive test names** - Test names should clearly indicate what is being tested
2. **Add assertion messages** - Include helpful messages for assertions to aid debugging
   ```python
   assert user is not None, f"User {user_id} should be found"
   ```
3. **Use fixtures** - Leverage fixtures to reduce code duplication
4. **Add docstrings** - Document what each test does
5. **Test edge cases** - Include tests for error conditions and boundary cases

### Example Test Structure

```python
@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_user_by_id(user_db_transaction):
    """Test retrieving user by ID."""
    # Setup - Create test data
    user_id = await create_user(...)
    
    # Action - Perform the operation
    user = await get_user_by_id(user_db_transaction, user_id)
    
    # Assert - Verify expected results with clear messages
    assert user is not None, f"User {user_id} should be found"
    assert user['user_id'] == user_id, "User ID should match"
```

## Debugging Failed Tests

When a test fails, the assertion messages will help identify the problem:

```
AssertionError: User 123e4567-e89b-12d3-a456-426614174000 should be found
```

This tells you:
1. Which assertion failed
2. The expected behavior
3. The relevant data (user ID)
