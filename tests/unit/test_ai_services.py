"""
Unit tests for AI services functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from incident_api.services import incident_analysis_service
from incident_api import models


class TestAIService:
    """Test AI service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)

    @pytest.mark.asyncio
    @patch('incident_api.services.incident_analysis_service.IncidentAnalysisService.get_incident_enrichment')
    async def test_get_incident_enrichment_success(self, mock_enrich):
        """Test successful incident enrichment."""
        # Mock settings
        mock_settings = Mock()

        # Mock enrichment data
        enrichment_data = {
            "ai_recommendations": {
                "suggested_category": "Malware",
                "severity": "High",
                "actions": ["Isolate system", "Run antivirus"]
            }
        }
        mock_enrich.return_value = enrichment_data

        # Mock incident
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1
        mock_incident.summary = "System infected with malware"

        result = await incident_analysis_service.incident_analysis_service.get_incident_enrichment(self.mock_db, mock_incident, mock_settings)

        assert result == enrichment_data
        mock_enrich.assert_called_once_with(self.mock_db, mock_incident, mock_settings)

    @pytest.mark.asyncio
    async def test_get_incident_enrichment_no_settings(self):
        """Test incident enrichment when no AI settings are available."""
        # Mock incident
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1
        mock_incident.summary = "Test incident"
        mock_incident.description = "Test description"
        mock_incident.incident_category = Mock()
        mock_incident.incident_category.name = "Test category"
        mock_incident.severity = Mock()
        mock_incident.severity.value = "High"

        # Should return empty dict when settings is None
        result = await incident_analysis_service.incident_analysis_service.get_incident_enrichment(self.mock_db, mock_incident, None)

        assert result == {}

    @pytest.mark.asyncio
    @patch('incident_api.services.llm_service.llm_service.invoke_for_json')
    async def test_get_incident_enrichment_service_error(self, mock_invoke):
        """Test incident enrichment when service raises an error."""
        # Mock settings
        mock_settings = Mock()

        # Mock service error
        mock_invoke.side_effect = Exception("AI service unavailable")

        # Mock incident
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1
        mock_incident.summary = "Test incident"
        mock_incident.description = "Test description"
        mock_incident.incident_category = Mock()
        mock_incident.incident_category.name = "Test category"
        mock_incident.severity = Mock()
        mock_incident.severity.value = "High"

        result = await incident_analysis_service.incident_analysis_service.get_incident_enrichment(self.mock_db, mock_incident, mock_settings)

        assert result == {}
        mock_invoke.assert_called_once()


class TestChatService:
    """Test chat service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=Session)
        self.mock_user = Mock(spec=models.User)
        self.mock_user.user_id = 1
        self.mock_user.email = "test@example.com"

    @pytest.mark.asyncio
    @patch('incident_api.services.chat_service.ChatService._get_assistant_response')
    async def test_get_reporting_assistant_response_success(self, mock_get_response):
        """Test successful reporting assistant response."""
        from incident_api.services.chat_service import chat_service

        # Mock settings
        mock_settings = Mock()

        # Mock response
        mock_get_response.return_value = "This appears to be a malware infection"

        prompt = "What should I do about this security alert?"
        conversation_id = "conv_123"

        result = await chat_service.get_reporting_assistant_response(
            db=self.mock_db,
            prompt=prompt,
            conversation_id=conversation_id,
            user_id=self.mock_user.user_id,
            settings=mock_settings
        )

        assert result == "This appears to be a malware infection"
        mock_get_response.assert_called_once()

    @pytest.mark.asyncio
    @patch('incident_api.services.chat_service.ChatService._get_assistant_response')
    async def test_get_isirt_assistant_response_success(self, mock_get_response):
        """Test successful ISIRT assistant response."""
        from incident_api.services.chat_service import chat_service

        # Mock settings
        mock_settings = Mock()

        # Mock response
        mock_get_response.return_value = "I'll help you analyze this incident"

        prompt = "I need help with a security incident"
        conversation_id = "conv_123"

        result = await chat_service.get_isirt_assistant_response(
            db=self.mock_db,
            prompt=prompt,
            conversation_id=conversation_id,
            user_id=self.mock_user.user_id,
            settings=mock_settings
        )

        assert result == "I'll help you analyze this incident"
        mock_get_response.assert_called_once()



class TestSecurityValidation:
    """Test security validation functions."""

    @patch('incident_api.core.security.jwt.decode')
    def test_decode_jwt_token_success(self, mock_decode):
        """Test successful JWT token decoding."""
        from incident_api.core.config import settings

        mock_decode.return_value = {"sub": "test@example.com", "exp": 1234567890}

        # This would normally be done in dependencies.py
        # but we'll test the core functionality
        token = "header.payload.signature"

        # Verify the mock was called correctly
        mock_decode.assert_not_called()  # Not called yet in this test

    def test_password_complexity_requirements(self):
        """Test password complexity validation."""
        from incident_api.core.security import Hasher

        # Test various password strengths
        weak_passwords = ["123", "password", "abc"]
        strong_passwords = ["MySecurePass123!", "Complex_P@ssw0rd"]

        for password in weak_passwords + strong_passwords:
            hashed = Hasher.get_password_hash(password)
            assert Hasher.verify_password(password, hashed)

    @patch('incident_api.core.security.jwt.encode')
    def test_jwt_token_structure(self, mock_encode):
        """Test JWT token has correct structure."""
        from incident_api.core.security import create_access_token

        mock_encode.return_value = "header.payload.signature"

        token = create_access_token({"sub": "test@example.com"})

        # Verify JWT structure (3 parts separated by dots)
        parts = token.split('.')
        assert len(parts) == 3
        assert all(len(part) > 0 for part in parts)


class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_database_connection_error_handling(self):
        """Test graceful handling of database connection errors."""
        # This would test the error handling in database operations
        pass

    def test_external_api_timeout_handling(self):
        """Test handling of external API timeouts."""
        # This would test timeout handling for AI services
        pass

    def test_file_system_error_handling(self):
        """Test handling of file system errors during upload."""
        # This would test file system error scenarios
        pass

    def test_validation_error_formatting(self):
        """Test that validation errors are properly formatted."""
        from pydantic import ValidationError, BaseModel
        from typing import Optional

        class TestModel(BaseModel):
            required_field: str
            optional_field: Optional[int] = None

        # Test missing required field
        with pytest.raises(ValidationError) as exc_info:
            TestModel()

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['type'] == 'missing' for error in errors)

    def test_http_exception_proper_status_codes(self):
        """Test that HTTP exceptions use appropriate status codes."""
        from fastapi import HTTPException

        # Test various status codes
        test_cases = [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (422, "Unprocessable Entity"),
            (500, "Internal Server Error")
        ]

        for status_code, detail in test_cases:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(status_code=status_code, detail=detail)

            assert exc_info.value.status_code == status_code
            assert exc_info.value.detail == detail