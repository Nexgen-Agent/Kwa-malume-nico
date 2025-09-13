"""
Basic tests for the authentication and user registration endpoints.
"""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_user_registration():
    """Test user registration endpoint with valid data."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "strongpassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "username" in data
        assert "email" in data

@pytest.mark.asyncio
async def test_duplicate_registration_fails():
    """Test that duplicate user registration fails."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration (should succeed)
        await client.post(
            "/auth/register",
            json={
                "username": "duplicateuser",
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )
        # Second registration with same username (should fail)
        response = await client.post(
            "/auth/register",
            json={
                "username": "duplicateuser",
                "email": "anotheremail@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 409 # HTTP 409 Conflict

@pytest.mark.asyncio
async def test_login_and_get_token():
    """Test user login and token generation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register a user first
        await client.post(
            "/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "loginpassword123"
            }
        )
        # Now try to log in
        response = await client.post(
            "/auth/login",
            data={
                "username": "loginuser",
                "password": "loginpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"