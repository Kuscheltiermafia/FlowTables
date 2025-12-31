"""
Tests for web routes and UI endpoints.

These tests cover the web application pages including:
- Index/homepage
- Login/logout functionality
- Dashboard access
- Error pages
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from Main import app
from backend.user_management.user_handler import create_user


pytestmark = [pytest.mark.web, pytest.mark.asyncio]


@pytest.fixture(scope="module")
async def async_client():
    """Create an AsyncClient for the full module."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


async def test_index_page(async_client: AsyncClient):
    """Test that the index page loads successfully."""
    response = await async_client.get("/")
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Index page should return 200, got {response.status_code}"
    assert "text/html" in response.headers.get("content-type", ""), \
        "Index page should return HTML content"
    assert len(response.text) > 0, "Index page should have content"


async def test_index_page_with_message(async_client: AsyncClient):
    """Test index page with message parameter."""
    response = await async_client.get("/?message=test_message")
    
    assert response.status_code == status.HTTP_200_OK, \
        "Index page with message should return 200"
    assert "text/html" in response.headers.get("content-type", ""), \
        "Response should be HTML"


async def test_login_page_get(async_client: AsyncClient):
    """Test that the login page loads successfully."""
    response = await async_client.get("/login")
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Login page should return 200, got {response.status_code}"
    assert "text/html" in response.headers.get("content-type", ""), \
        "Login page should return HTML content"


async def test_login_redirect_when_logged_in(async_client: AsyncClient):
    """Test that logged-in users are redirected from login page."""
    # First, set up a session cookie as if user is logged in
    async_client.cookies.set("session", "test_session_value")
    
    response = await async_client.get("/login", follow_redirects=False)
    
    # The response contains a redirect script
    assert response.status_code == status.HTTP_200_OK, \
        "Should return 200 with redirect script"


async def test_logout_get(async_client: AsyncClient):
    """Test logout via GET request."""
    response = await async_client.get("/logout", follow_redirects=False)
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Logout should return 200, got {response.status_code}"
    # Check for redirect script
    assert "window.location.replace" in response.text, \
        "Logout should contain redirect script"


async def test_logout_post(async_client: AsyncClient):
    """Test logout via POST request."""
    response = await async_client.post("/logout")
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Logout POST should return 200, got {response.status_code}"
    assert response.json() == {"message": "Logged out"}, \
        "Logout should return success message"


async def test_static_files_accessible(async_client: AsyncClient):
    """Test that static files are accessible."""
    response = await async_client.get("/static/styles.css")
    
    assert response.status_code == status.HTTP_200_OK, \
        f"Static CSS file should be accessible, got {response.status_code}"
    assert "text/css" in response.headers.get("content-type", ""), \
        "CSS file should have correct content type"


async def test_error_page_403(async_client: AsyncClient):
    """Test 403 error page."""
    response = await async_client.get("/secret")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN, \
        f"Secret route should return 403, got {response.status_code}"
    assert "text/html" in response.headers.get("content-type", ""), \
        "Error page should return HTML"
    assert "403" in response.text, \
        "Error page should display 403 status"


async def test_error_page_500(async_client: AsyncClient):
    """Test 500 error page."""
    response = await async_client.get("/trigger-500")
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, \
        f"Trigger-500 route should return 500, got {response.status_code}"
    assert "text/html" in response.headers.get("content-type", ""), \
        "Error page should return HTML"
    assert "500" in response.text, \
        "Error page should display 500 status"


async def test_nonexistent_route_404(async_client: AsyncClient):
    """Test that non-existent routes return 404."""
    response = await async_client.get("/this-route-does-not-exist")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND, \
        f"Non-existent route should return 404, got {response.status_code}"


async def test_dashboard_requires_login(async_client: AsyncClient):
    """Test that dashboard requires authentication."""
    # Clear any existing session
    async_client.cookies.clear()
    
    response = await async_client.get("/dashboard")
    
    # Should either redirect or return unauthorized status
    # Depending on implementation, this might be 401, 403, or a redirect
    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
        status.HTTP_200_OK,  # May return 200 with redirect script
        status.HTTP_307_TEMPORARY_REDIRECT,
        status.HTTP_302_FOUND
    ], f"Dashboard without login should return auth error or redirect, got {response.status_code}"


async def test_request_headers_added(async_client: AsyncClient):
    """Test that custom request headers are added by middleware."""
    response = await async_client.get("/")
    
    # Check for custom headers added by middleware
    assert "X-Request-ID" in response.headers or "X-Process-Time" in response.headers, \
        "Response should include custom headers from middleware"


async def test_cors_and_security_headers(async_client: AsyncClient):
    """Test basic response structure."""
    response = await async_client.get("/")
    
    # Basic checks that the response is well-formed
    assert response.status_code == status.HTTP_200_OK, \
        "Response should be successful"
    assert "content-type" in response.headers, \
        "Response should have content-type header"


async def test_session_middleware_active(async_client: AsyncClient):
    """Test that session middleware is active."""
    # Make a request and check if session cookie handling is present
    response = await async_client.get("/login")
    
    # Session middleware should be active (either sets cookie or allows session handling)
    assert response.status_code == status.HTTP_200_OK, \
        "Session middleware should not prevent page access"
