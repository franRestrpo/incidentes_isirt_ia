"""
Unit tests for authentication functionality.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from incident_api.core import security
from incident_api import crud, models
from incident_api.schemas import UserCreate
from incident_api.models import UserRole


class TestAuthentication:
    """Test authentication functions."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com", "role": "ADMINISTRADOR"}

        token = security.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
        # Token should be a valid JWT (3 parts separated by dots)
        assert len(token.split('.')) == 3

    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry."""
        from datetime import timedelta

        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)

        token = security.create_access_token(data, expires_delta)

        assert isinstance(token, str)
        assert len(token.split('.')) == 3

    @patch('incident_api.crud.user.get_by_email')
    def test_authenticate_user_success(self, mock_get_by_email):
        """Test successful user authentication."""
        # Mock user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = security.Hasher.get_password_hash("password123")
        mock_user.is_active = True

        mock_get_by_email.return_value = mock_user

        # Mock session
        mock_db = Mock(spec=Session)

        result = security.authenticate_user(mock_db, "test@example.com", "password123")

        assert result == mock_user
        mock_get_by_email.assert_called_once_with(mock_db, email="test@example.com")

    @patch('incident_api.crud.user.get_by_email')
    def test_authenticate_user_wrong_password(self, mock_get_by_email):
        """Test authentication with wrong password."""
        # Mock user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = security.Hasher.get_password_hash("correct_password")
        mock_user.is_active = True

        mock_get_by_email.return_value = mock_user

        # Mock session
        mock_db = Mock(spec=Session)

        result = security.authenticate_user(mock_db, "test@example.com", "wrong_password")

        assert result is None

    @patch('incident_api.crud.user.get_by_email')
    def test_authenticate_user_inactive(self, mock_get_by_email):
        """Test authentication with inactive user."""
        # Mock inactive user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = security.Hasher.get_password_hash("password123")
        mock_user.is_active = False

        mock_get_by_email.return_value = mock_user

        # Mock session
        mock_db = Mock(spec=Session)

        result = security.authenticate_user(mock_db, "test@example.com", "password123")

        assert result is None

    @patch('incident_api.crud.user.get_by_email')
    def test_authenticate_user_not_found(self, mock_get_by_email):
        """Test authentication with non-existent user."""
        mock_get_by_email.return_value = None

        # Mock session
        mock_db = Mock(spec=Session)

        result = security.authenticate_user(mock_db, "nonexistent@example.com", "password123")

        assert result is None


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_password_hash_creation(self):
        """Test that password hashing creates different hashes for same password."""
        password = "test_password_123"

        hash1 = security.Hasher.get_password_hash(password)
        hash2 = security.Hasher.get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)

    def test_password_verification(self):
        """Test password verification."""
        password = "my_secure_password"
        hashed = security.Hasher.get_password_hash(password)

        # Should verify correctly
        assert security.Hasher.verify_password(password, hashed)

        # Should fail with wrong password
        assert not security.Hasher.verify_password("wrong_password", hashed)

    def test_password_verification_wrong_hash(self):
        """Test password verification with invalid hash."""
        password = "test_password"

        # Should fail with invalid hash
        assert not security.Hasher.verify_password(password, "invalid_hash")


class TestUserCRUD:
    """Test user CRUD operations."""

    @patch('incident_api.crud.user.create')
    def test_create_user_success(self, mock_create):
        """Test successful user creation."""
        # Mock the created user
        mock_user = Mock()
        mock_user.user_id = 1
        mock_user.email = "newuser@example.com"
        mock_user.full_name = "New User"
        mock_create.return_value = mock_user

        # Mock session
        mock_db = Mock(spec=Session)

        user_data = UserCreate(
            email="newuser@example.com",
            password="secure_password",
            full_name="New User",
            role=UserRole.MIEMBRO_IRT
        )

        result = crud.user.create(mock_db, obj_in=user_data)

        assert result == mock_user
        mock_create.assert_called_once_with(mock_db, obj_in=user_data)

    @patch('incident_api.crud.user.get_by_email')
    def test_get_user_by_email_found(self, mock_get_by_email):
        """Test getting user by email when found."""
        # Mock user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.user_id = 1

        mock_get_by_email.return_value = mock_user

        # Mock session
        mock_db = Mock(spec=Session)

        result = crud.user.get_by_email(mock_db, email="test@example.com")

        assert result == mock_user
        mock_get_by_email.assert_called_once_with(mock_db, email="test@example.com")

    @patch('incident_api.crud.user.get_by_email')
    def test_get_user_by_email_not_found(self, mock_get_by_email):
        """Test getting user by email when not found."""
        mock_get_by_email.return_value = None

        # Mock session
        mock_db = Mock(spec=Session)

        result = crud.user.get_by_email(mock_db, email="nonexistent@example.com")

        assert result is None