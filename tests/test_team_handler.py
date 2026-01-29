import pytest
from backend.user_management.team_handler import (
    create_team, get_team_by_id, get_team_by_name, delete_team
)


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_create_team(user_db_transaction):
    """Test creating a team."""
    team_id = await create_team(user_db_transaction, "New Test Team")
    
    assert team_id is not None, "Team ID should be returned after creation"
    
    # Verify team was created
    result = await user_db_transaction.fetchrow(
        'SELECT * FROM teams WHERE team_id = $1',
        team_id
    )
    assert result is not None, f"Team {team_id} should exist in database"
    assert result['team_name'] == "New Test Team", \
        f"Team name should be 'New Test Team', got '{result['team_name']}'"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_team_by_id(user_db_transaction):
    """Test retrieving a team by ID."""
    # Create a team
    team_id = await create_team(user_db_transaction, "Get By ID Team")
    
    # Get team by ID
    team = await get_team_by_id(user_db_transaction, team_id)
    
    assert team is not None, f"Team {team_id} should be found"
    assert team['team_id'] == team_id, "Team ID should match"
    assert team['team_name'] == "Get By ID Team", \
        f"Team name should be 'Get By ID Team', got '{team['team_name']}'"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_team_by_id_not_found(user_db_transaction):
    """Test retrieving non-existent team by ID."""
    from uuid import uuid4
    non_existent_id = uuid4()
    team = await get_team_by_id(user_db_transaction, non_existent_id)
    assert team is None, f"Non-existent team ID {non_existent_id} should return None"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_team_by_name(user_db_transaction):
    """Test retrieving a team by name."""
    # Create a team
    team_id = await create_team(user_db_transaction, "Get By Name Team")
    
    # Get team by name
    team = await get_team_by_name(user_db_transaction, "Get By Name Team")
    
    assert team is not None, "Team 'Get By Name Team' should be found"
    assert team['team_id'] == team_id, "Team ID should match"
    assert team['team_name'] == "Get By Name Team", "Team name should match"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_get_team_by_name_not_found(user_db_transaction):
    """Test retrieving non-existent team by name."""
    team = await get_team_by_name(user_db_transaction, "Nonexistent Team")
    assert team is None, "Non-existent team name should return None"


@pytest.mark.user_creation
@pytest.mark.asyncio
async def test_delete_team(user_db_transaction):
    """Test deleting a team."""
    # Create a team
    team_id = await create_team(user_db_transaction, "Delete Test Team")
    
    # Verify team exists
    team = await get_team_by_id(user_db_transaction, team_id)
    assert team is not None, "Team should exist before deletion"
    
    # Delete team
    await delete_team(user_db_transaction, team_id)
    
    # Verify team is deleted
    team = await get_team_by_id(user_db_transaction, team_id)
    assert team is None, f"Team {team_id} should be deleted"
