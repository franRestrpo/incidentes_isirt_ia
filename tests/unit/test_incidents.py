"""
Unit tests for incident-related functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from incident_api import models, schemas
from incident_api.services.incident_service import IncidentService
from incident_api.services.change_logging_service import change_logging_service
from incident_api.api.dependencies import validate_status_change_permission
from incident_api.models import IncidentStatus, UserRole


class TestIncidentService:
    """Test IncidentService methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.incident_service = IncidentService()
        self.mock_db = Mock(spec=Session)
        self.mock_user = Mock(spec=models.User)
        self.mock_user.user_id = 1
        self.mock_user.email = "test@example.com"
        self.mock_user.role = UserRole.MIEMBRO_IRT

    @patch('incident_api.crud.incident.get')
    def test_get_incident_by_id_found(self, mock_get):
        """Test getting incident by ID when found."""
        # Mock incident
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1
        mock_incident.summary = "Test incident"
        mock_get.return_value = mock_incident

        result = self.incident_service.get_incident_by_id(self.mock_db, 1)

        assert result == mock_incident
        mock_get.assert_called_once_with(self.mock_db, id=1)

    @patch('incident_api.crud.incident.get')
    def test_get_incident_by_id_not_found(self, mock_get):
        """Test getting incident by ID when not found."""
        mock_get.return_value = None

        result = self.incident_service.get_incident_by_id(self.mock_db, 999)

        assert result is None

    @patch('incident_api.crud.incident.get_multi')
    def test_get_all_incidents(self, mock_get_multi):
        """Test getting all incidents."""
        mock_incidents = [Mock(spec=models.Incident) for _ in range(3)]
        mock_get_multi.return_value = mock_incidents

        result = self.incident_service.get_all_incidents(self.mock_db, skip=0, limit=10)

        assert result == mock_incidents
        mock_get_multi.assert_called_once_with(self.mock_db, skip=0, limit=10)

    @pytest.mark.asyncio
    @patch('incident_api.schemas.IncidentCreateFromString.validate_json')
    @patch.object(IncidentService, 'create_incident')
    async def test_create_incident_from_json_string_success(self, mock_create_incident, mock_validate):
        """Test successful incident creation from JSON string."""
        json_string = '{"summary": "Test incident", "description": "Test description"}'
        mock_incident_data = Mock()
        mock_validate.return_value = mock_incident_data

        mock_created_incident = Mock(spec=models.Incident)
        mock_create_incident.return_value = mock_created_incident

        result = await self.incident_service.create_incident_from_json_string(
            self.mock_db, incident_data_str=json_string, user=self.mock_user
        )

        assert result == mock_created_incident
        mock_validate.assert_called_once_with(json_string)
        mock_create_incident.assert_called_once_with(
            self.mock_db, incident_in=mock_incident_data, user=self.mock_user, evidence_files=None
        )

    @pytest.mark.asyncio
    @patch('incident_api.schemas.IncidentCreateFromString.validate_json')
    async def test_create_incident_from_json_string_invalid_json(self, mock_validate):
        """Test incident creation from invalid JSON string."""
        from pydantic import ValidationError

        json_string = 'invalid json'
        mock_validate.side_effect = ValidationError.from_exception_data(
            title="ValidationError",
            line_errors=[]
        )

        with pytest.raises(Exception):  # Should raise HTTPException
            await self.incident_service.create_incident_from_json_string(
                self.mock_db, incident_data_str=json_string, user=self.mock_user
            )

    @pytest.mark.asyncio
    @patch('incident_api.crud.incident.create')
    @patch.object(IncidentService, '_handle_evidence_upload')
    @patch.object(IncidentService, '_log_incident_creation')
    @patch.object(IncidentService, '_enrich_incident_with_ai')
    async def test_create_incident_success(self, mock_enrich, mock_log, mock_handle_upload, mock_create):
        """Test successful incident creation."""
        # Mock incident data
        incident_data = schemas.IncidentCreate(
            summary="Test incident",
            description="Test description",
            discovery_time=datetime.now(timezone.utc)
        )

        # Mock created incident
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1
        mock_create.return_value = mock_incident

        result = await self.incident_service.create_incident(
            self.mock_db, incident_in=incident_data, user=self.mock_user
        )

        assert result == mock_incident
        mock_create.assert_called_once_with(
            self.mock_db, obj_in=incident_data, reported_by_id=self.mock_user.user_id
        )
        # _handle_evidence_upload is not called when evidence_files is None
        mock_handle_upload.assert_not_called()
        mock_log.assert_called_once_with(self.mock_db, mock_incident, self.mock_user)
        mock_enrich.assert_called_once_with(self.mock_db, mock_incident)

    @pytest.mark.asyncio
    @patch('incident_api.crud.incident.create')
    @patch.object(IncidentService, '_handle_evidence_upload')
    @patch.object(IncidentService, '_log_incident_creation')
    @patch.object(IncidentService, '_enrich_incident_with_ai')
    async def test_create_incident_with_files(self, mock_enrich, mock_log, mock_handle_upload, mock_create):
        """Test incident creation with evidence files."""
        # Mock incident data
        incident_data = schemas.IncidentCreate(
            summary="Test incident with files",
            description="Test description",
            discovery_time=datetime.now(timezone.utc)
        )

        # Mock files
        mock_files = [Mock(), Mock()]

        # Mock created incident
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1
        mock_create.return_value = mock_incident

        result = await self.incident_service.create_incident(
            self.mock_db, incident_in=incident_data, user=self.mock_user, evidence_files=mock_files
        )

        assert result == mock_incident
        mock_handle_upload.assert_called_once_with(
            self.mock_db, incident=mock_incident, files=mock_files, uploader=self.mock_user
        )

    def test_validate_status_change_permission_admin(self):
        """Test status change permission for admin user."""
        admin_user = Mock(spec=models.User)
        admin_user.role = UserRole.ADMINISTRADOR

        mock_incident = Mock(spec=models.Incident)
        mock_incident.status = IncidentStatus.NUEVO

        # Should not raise exception
        validate_status_change_permission(
            admin_user, mock_incident, IncidentStatus.CERRADO
        )

    def test_validate_status_change_permission_irt_leader(self):
        """Test status change permission for IRT leader."""
        leader_user = Mock(spec=models.User)
        leader_user.role = UserRole.LIDER_IRT

        mock_incident = Mock(spec=models.Incident)
        mock_incident.status = IncidentStatus.NUEVO

        # Should not raise exception
        validate_status_change_permission(
            leader_user, mock_incident, IncidentStatus.CERRADO
        )

    def test_validate_status_change_permission_irt_member(self):
        """Test status change permission for IRT member."""
        member_user = Mock(spec=models.User)
        member_user.role = UserRole.MIEMBRO_IRT

        mock_incident = Mock(spec=models.Incident)
        mock_incident.status = IncidentStatus.NUEVO

        # Should not raise exception for non-closed status
        validate_status_change_permission(
            member_user, mock_incident, IncidentStatus.INVESTIGANDO
        )

    def test_validate_status_change_permission_regular_user_denied(self):
        """Test status change permission denied for regular user."""
        from fastapi import HTTPException

        regular_user = Mock(spec=models.User)
        regular_user.role = UserRole.EMPLEADO  # Regular employee role

        mock_incident = Mock(spec=models.Incident)
        mock_incident.status = IncidentStatus.NUEVO

        with pytest.raises(HTTPException) as exc_info:
            validate_status_change_permission(
                regular_user, mock_incident, IncidentStatus.INVESTIGANDO
            )

        assert exc_info.value.status_code == 403

    def test_validate_status_change_permission_close_closed_incident(self):
        """Test that non-admin/leader cannot modify closed incidents."""
        from fastapi import HTTPException

        member_user = Mock(spec=models.User)
        member_user.role = UserRole.MIEMBRO_IRT

        mock_incident = Mock(spec=models.Incident)
        mock_incident.status = IncidentStatus.CERRADO

        with pytest.raises(HTTPException) as exc_info:
            validate_status_change_permission(
                member_user, mock_incident, IncidentStatus.INVESTIGANDO
            )

        assert exc_info.value.status_code == 403

    @patch('incident_api.crud.incident_log.create_with_incident_and_user')
    def test_log_changes_field_modified(self, mock_create_log):
        """Test logging of field changes."""
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1

        # Mock user
        mock_user = Mock(spec=models.User)
        mock_user.user_id = 1
        mock_user.email = "test@example.com"

        # Mock updates
        updates = {"summary": "New summary", "status": IncidentStatus.INVESTIGANDO}

        change_logging_service.log_changes(self.mock_db, original_incident=mock_incident, updates=updates, user=mock_user)

        # Should create log entries for each changed field
        assert mock_create_log.call_count == 2

        # Check first call (summary change)
        first_call = mock_create_log.call_args_list[0]
        log_data = first_call[1]['obj_in']
        assert log_data.action == "Actualización de Campo"
        assert log_data.field_modified == "summary"
        assert "New summary" in log_data.new_value

    @patch('incident_api.crud.incident_log.create_with_incident_and_user')
    def test_log_changes_no_changes(self, mock_create_log):
        """Test that no log is created when no changes are made."""
        mock_incident = Mock(spec=models.Incident)
        mock_incident.incident_id = 1
        mock_incident.summary = "Test summary"
        mock_incident.status = IncidentStatus.NUEVO

        mock_user = Mock(spec=models.User)
        mock_user.user_id = 1
        mock_user.email = "test@example.com"

        # Same values, no changes
        updates = {"summary": "Test summary", "status": IncidentStatus.NUEVO}

        change_logging_service.log_changes(self.mock_db, original_incident=mock_incident, updates=updates, user=mock_user)

        # Should not create any log entries
        mock_create_log.assert_not_called()


class TestIncidentSchemas:
    """Test Pydantic schemas for incidents."""

    def test_incident_create_valid(self):
        """Test valid IncidentCreate schema."""
        from datetime import datetime, timezone

        data = {
            "summary": "Test incident summary",
            "description": "Detailed description of the incident",
            "discovery_time": datetime.now(timezone.utc),
            "asset_id": 1,
            "incident_type_id": 2,
            "attack_vector_id": 3,
            "other_asset_location": "Server room A"
        }

        incident = schemas.IncidentCreate(**data)

        assert incident.summary == data["summary"]
        assert incident.description == data["description"]
        assert incident.asset_id == data["asset_id"]
        assert incident.incident_type_id == data["incident_type_id"]
        assert incident.attack_vector_id == data["attack_vector_id"]
        assert incident.other_asset_location == data["other_asset_location"]

    def test_incident_create_missing_required(self):
        """Test IncidentCreate with missing required fields."""
        from pydantic import ValidationError

        # Missing required fields
        data = {
            "description": "Missing summary and discovery_time"
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.IncidentCreate(**data)

        errors = exc_info.value.errors()
        assert len(errors) >= 2  # At least summary and discovery_time missing

    def test_incident_create_invalid_length(self):
        """Test IncidentCreate with invalid field lengths."""
        from pydantic import ValidationError
        from datetime import datetime, timezone

        # Summary too long
        data = {
            "summary": "x" * 256,  # Max length is 255
            "description": "Valid description",
            "discovery_time": datetime.now(timezone.utc)
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.IncidentCreate(**data)

        assert "summary" in str(exc_info.value)

    def test_incident_update_optional_fields(self):
        """Test IncidentUpdate with only optional fields."""
        data = {
            "summary": "Updated summary"
        }

        update = schemas.IncidentUpdate(**data)

        assert update.summary == data["summary"]
        assert update.description is None
        assert update.status is None

    def test_incident_update_invalid_impact_values(self):
        """Test IncidentUpdate with invalid impact values."""
        from pydantic import ValidationError

        # Impact values out of range
        data = {
            "impact_confidentiality": 15,  # Max is 10
            "impact_integrity": -1,        # Min is 0
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.IncidentUpdate(**data)

        errors = exc_info.value.errors()
        assert len(errors) > 0