
import pytest
from httpx import AsyncClient
from fastapi import status
from main import app # Import your FastAPI app

# Mark all tests in this file as async-capable
pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="module")
async def async_client():
    """Create an AsyncClient for the full module."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

async def test_create_user_success(async_client: AsyncClient):
    """Test successful user creation."""
    user_data = {
        "user_name": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "aSecurePassword123"
    }
    response = await async_client.post("/api/v1/users", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    
    response_data = response.json()
    assert response_data["user_name"] == user_data["user_name"]
    assert response_data["email"] == user_data["email"]
    assert "password" not in response_data # Ensure password is not returned

async def test_create_user_conflict(async_client: AsyncClient):
    """Test user creation conflict (duplicate username/email)."""
    # First, create a user
    user_data = {
        "user_name": "conflictuser",
        "first_name": "Conflict",
        "last_name": "User",
        "email": "conflict@example.com",
        "password": "aSecurePassword123"
    }
    response1 = await async_client.post("/api/v1/users", json=user_data)
    assert response1.status_code == status.HTTP_201_CREATED

    # Then, try to create the same user again
    response2 = await async_client.post("/api/v1/users", json=user_data)
    assert response2.status_code == status.HTTP_409_CONFLICT
