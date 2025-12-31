import pytest
from backend.user_management.user_handler import (
    create_user, verify_password, hash_password, valid_password,
    get_user_by_id, get_user_by_username, delete_user,
    add_user_to_team, remove_user_from_team
)
from backend.user_management.team_handler import create_team


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_hash_and_verify_password():
    """Test password hashing and verification."""
    plain_password = "Test1234!"
    hashed = hash_password(plain_password)
    
    # Verify correct password
    assert verify_password(plain_password, hashed)
    
    # Verify incorrect password
    assert not verify_password("WrongPassword", hashed)


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_valid_password_with_username(user_db_transaction):
    """Test password validation with username."""
    # Create a test user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="password_test_user",
        email="password@test.com",
        password="SecurePass123!",
        lastName="Test",
        firstName="Password"
    )
    
    # Test valid password with username
    assert await valid_password(user_db_transaction, "password_test_user", "SecurePass123!")
    
    # Test invalid password
    assert not await valid_password(user_db_transaction, "password_test_user", "WrongPassword")
    
    # Test with non-existent user
    assert not await valid_password(user_db_transaction, "nonexistent_user", "SecurePass123!")


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_valid_password_with_email(user_db_transaction):
    """Test password validation with email."""
    # Create a test user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="email_test_user",
        email="email@test.com",
        password="SecurePass123!",
        lastName="Test",
        firstName="Email"
    )
    
    # Test valid password with email
    assert await valid_password(user_db_transaction, "email@test.com", "SecurePass123!")
    
    # Test invalid password
    assert not await valid_password(user_db_transaction, "email@test.com", "WrongPassword")


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_valid_password_with_none_values(user_db_transaction):
    """Test password validation with None values."""
    assert not await valid_password(user_db_transaction, None, "password")
    assert not await valid_password(user_db_transaction, "username", None)
    assert not await valid_password(user_db_transaction, None, None)


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_user_by_id(user_db_transaction):
    """Test retrieving user by ID."""
    # Create a test user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="id_test_user",
        email="id@test.com",
        password="SecurePass123!",
        lastName="TestLast",
        firstName="TestFirst"
    )
    
    # Get user by ID
    user = await get_user_by_id(user_db_transaction, user_id)
    
    assert user is not None
    assert user['user_id'] == user_id
    assert user['username'] == "id_test_user"
    assert user['email'] == "id@test.com"
    assert user['lastname'] == "TestLast"
    assert user['firstname'] == "TestFirst"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_db_transaction):
    """Test retrieving non-existent user by ID."""
    from uuid import uuid4
    non_existent_id = uuid4()
    user = await get_user_by_id(user_db_transaction, non_existent_id)
    assert user is None


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_user_by_username(user_db_transaction):
    """Test retrieving user by username."""
    # Create a test user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="username_test_user",
        email="username@test.com",
        password="SecurePass123!",
        lastName="TestLast",
        firstName="TestFirst"
    )
    
    # Get user by username
    user = await get_user_by_username(user_db_transaction, "username_test_user")
    
    assert user is not None
    assert user['user_id'] == user_id
    assert user['username'] == "username_test_user"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_user_by_username_not_found(user_db_transaction):
    """Test retrieving non-existent user by username."""
    user = await get_user_by_username(user_db_transaction, "nonexistent_username")
    assert user is None


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_delete_user(user_db_transaction):
    """Test deleting a user."""
    # Create a test user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="delete_test_user",
        email="delete@test.com",
        password="SecurePass123!",
        lastName="Delete",
        firstName="Test"
    )
    
    # Verify user exists
    user = await get_user_by_id(user_db_transaction, user_id)
    assert user is not None
    
    # Delete user
    await delete_user(user_db_transaction, user_id)
    
    # Verify user is deleted
    user = await get_user_by_id(user_db_transaction, user_id)
    assert user is None


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_add_user_to_team(user_db_transaction):
    """Test adding a user to a team."""
    # Create a test user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="team_member_user",
        email="member@test.com",
        password="SecurePass123!",
        lastName="Member",
        firstName="Team"
    )
    
    # Create a team
    team_id = await create_team(user_db_transaction, "Test Team")
    
    # Add user to team
    await add_user_to_team(user_db_transaction, user_id, team_id, "member")
    
    # Verify user is in team
    result = await user_db_transaction.fetchrow(
        'SELECT * FROM team_members WHERE user_id = $1 AND team_id = $2',
        user_id, team_id
    )
    assert result is not None
    assert result['role'] == "member"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_remove_user_from_team(user_db_transaction):
    """Test removing a user from a team."""
    # Create a test user
    user_id = await create_user(
        user_connection=user_db_transaction,
        userName="remove_team_user",
        email="remove@test.com",
        password="SecurePass123!",
        lastName="Remove",
        firstName="Team"
    )
    
    # Create a team
    team_id = await create_team(user_db_transaction, "Remove Test Team")
    
    # Add user to team
    await add_user_to_team(user_db_transaction, user_id, team_id, "member")
    
    # Verify user is in team
    result = await user_db_transaction.fetchrow(
        'SELECT * FROM team_members WHERE user_id = $1 AND team_id = $2',
        user_id, team_id
    )
    assert result is not None
    
    # Remove user from team
    await remove_user_from_team(user_db_transaction, user_id, team_id)
    
    # Verify user is removed from team
    result = await user_db_transaction.fetchrow(
        'SELECT * FROM team_members WHERE user_id = $1 AND team_id = $2',
        user_id, team_id
    )
    assert result is None


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_create_user_validation(user_db_transaction):
    """Test user creation validation."""
    # Test empty username
    with pytest.raises(ValueError, match="Username, email, and password cannot be empty"):
        await create_user(
            user_connection=user_db_transaction,
            userName="",
            email="test@test.com",
            password="password",
            lastName="Last",
            firstName="First"
        )
    
    # Test empty email
    with pytest.raises(ValueError, match="Username, email, and password cannot be empty"):
        await create_user(
            user_connection=user_db_transaction,
            userName="username",
            email="",
            password="password",
            lastName="Last",
            firstName="First"
        )
    
    # Test empty password
    with pytest.raises(ValueError, match="Username, email, and password cannot be empty"):
        await create_user(
            user_connection=user_db_transaction,
            userName="username",
            email="test@test.com",
            password="",
            lastName="Last",
            firstName="First"
        )


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_create_user_duplicate(user_db_transaction):
    """Test duplicate user creation."""
    # Create first user
    await create_user(
        user_connection=user_db_transaction,
        userName="duplicate_user",
        email="duplicate@test.com",
        password="password",
        lastName="Last",
        firstName="First"
    )
    
    # Try to create with same username
    with pytest.raises(ValueError, match="Username or email already exists"):
        await create_user(
            user_connection=user_db_transaction,
            userName="duplicate_user",
            email="different@test.com",
            password="password",
            lastName="Last",
            firstName="First"
        )
    
    # Try to create with same email
    with pytest.raises(ValueError, match="Username or email already exists"):
        await create_user(
            user_connection=user_db_transaction,
            userName="different_user",
            email="duplicate@test.com",
            password="password",
            lastName="Last",
            firstName="First"
        )
