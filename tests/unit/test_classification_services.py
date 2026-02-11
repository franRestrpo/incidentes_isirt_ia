"""
Unit tests for classification-related services.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from incident_api import models, schemas
from incident_api.services.asset_type_service import AssetTypeService
from incident_api.services.asset_service import AssetService
from incident_api.services.incident_category_service import IncidentCategoryService
from incident_api.services.incident_type_service import IncidentTypeService
from incident_api.services.attack_vector_service import AttackVectorService


class TestAssetTypeService:
    """Test AssetTypeService methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssetTypeService()
        self.mock_db = Mock(spec=Session)

    @patch('incident_api.crud.asset_type.get')
    def test_get_asset_type_by_id_found(self, mock_get):
        """Test getting asset type by ID when found."""
        mock_asset_type = Mock(spec=models.AssetType)
        mock_asset_type.id = 1
        mock_asset_type.name = "Test Asset Type"
        mock_get.return_value = mock_asset_type

        result = self.service.get_asset_type_by_id(self.mock_db, 1)

        assert result == mock_asset_type
        mock_get.assert_called_once_with(self.mock_db, id=1)

    @patch('incident_api.crud.asset_type.get')
    def test_get_asset_type_by_id_not_found(self, mock_get):
        """Test getting asset type by ID when not found."""
        mock_get.return_value = None

        result = self.service.get_asset_type_by_id(self.mock_db, 999)

        assert result is None

    @patch('incident_api.crud.asset_type.get_multi')
    def test_get_all_asset_types(self, mock_get_multi):
        """Test getting all asset types."""
        mock_asset_types = [Mock(spec=models.AssetType) for _ in range(3)]
        mock_get_multi.return_value = mock_asset_types

        result = self.service.get_all_asset_types(self.mock_db, skip=0, limit=10)

        assert result == mock_asset_types
        mock_get_multi.assert_called_once_with(self.mock_db, skip=0, limit=10)

    @patch('incident_api.crud.asset_type.create')
    def test_create_asset_type(self, mock_create):
        """Test creating an asset type."""
        asset_type_data = schemas.AssetTypeCreate(name="New Asset Type", description="Description")
        mock_created_asset_type = Mock(spec=models.AssetType)
        mock_create.return_value = mock_created_asset_type

        result = self.service.create_asset_type(self.mock_db, asset_type_data)

        assert result == mock_created_asset_type
        mock_create.assert_called_once_with(self.mock_db, obj_in=asset_type_data)


class TestAssetService:
    """Test AssetService methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssetService()
        self.mock_db = Mock(spec=Session)

    @patch('incident_api.crud.asset.get')
    def test_get_asset_by_id_found(self, mock_get):
        """Test getting asset by ID when found."""
        mock_asset = Mock(spec=models.Asset)
        mock_asset.id = 1
        mock_asset.name = "Test Asset"
        mock_get.return_value = mock_asset

        result = self.service.get_asset_by_id(self.mock_db, 1)

        assert result == mock_asset
        mock_get.assert_called_once_with(self.mock_db, id=1)

    @patch('incident_api.crud.asset.get')
    def test_get_asset_by_id_not_found(self, mock_get):
        """Test getting asset by ID when not found."""
        mock_get.return_value = None

        result = self.service.get_asset_by_id(self.mock_db, 999)

        assert result is None

    @patch('incident_api.crud.asset.get_multi')
    def test_get_all_assets(self, mock_get_multi):
        """Test getting all assets."""
        mock_assets = [Mock(spec=models.Asset) for _ in range(3)]
        mock_get_multi.return_value = mock_assets

        result = self.service.get_all_assets(self.mock_db, skip=0, limit=10)

        assert result == mock_assets
        mock_get_multi.assert_called_once_with(self.mock_db, skip=0, limit=10)

    @patch('incident_api.crud.asset.create')
    def test_create_asset(self, mock_create):
        """Test creating an asset."""
        asset_data = schemas.AssetCreate(name="New Asset", asset_type_id=1, description="Description")
        mock_created_asset = Mock(spec=models.Asset)
        mock_create.return_value = mock_created_asset

        result = self.service.create_asset(self.mock_db, asset_data)

        assert result == mock_created_asset
        mock_create.assert_called_once_with(self.mock_db, obj_in=asset_data)


class TestIncidentCategoryService:
    """Test IncidentCategoryService methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = IncidentCategoryService()
        self.mock_db = Mock(spec=Session)

    @patch('incident_api.crud.incident_category.get')
    def test_get_incident_category_by_id_found(self, mock_get):
        """Test getting incident category by ID when found."""
        mock_category = Mock(spec=models.IncidentCategory)
        mock_category.id = 1
        mock_category.name = "Test Category"
        mock_get.return_value = mock_category

        result = self.service.get_incident_category_by_id(self.mock_db, 1)

        assert result == mock_category
        mock_get.assert_called_once_with(self.mock_db, id=1)

    @patch('incident_api.crud.incident_category.get')
    def test_get_incident_category_by_id_not_found(self, mock_get):
        """Test getting incident category by ID when not found."""
        mock_get.return_value = None

        result = self.service.get_incident_category_by_id(self.mock_db, 999)

        assert result is None

    @patch('incident_api.crud.incident_category.get_multi')
    def test_get_all_incident_categories(self, mock_get_multi):
        """Test getting all incident categories."""
        mock_categories = [Mock(spec=models.IncidentCategory) for _ in range(3)]
        mock_get_multi.return_value = mock_categories

        result = self.service.get_all_incident_categories(self.mock_db, skip=0, limit=10)

        assert result == mock_categories
        mock_get_multi.assert_called_once_with(self.mock_db, skip=0, limit=10)

    @patch('incident_api.crud.incident_category.create')
    def test_create_incident_category(self, mock_create):
        """Test creating an incident category."""
        category_data = schemas.IncidentCategoryCreate(name="New Category", description="Description")
        mock_created_category = Mock(spec=models.IncidentCategory)
        mock_create.return_value = mock_created_category

        result = self.service.create_incident_category(self.mock_db, category_data)

        assert result == mock_created_category
        mock_create.assert_called_once_with(self.mock_db, obj_in=category_data)


class TestIncidentTypeService:
    """Test IncidentTypeService methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = IncidentTypeService()
        self.mock_db = Mock(spec=Session)

    @patch('incident_api.crud.incident_type.get')
    def test_get_incident_type_by_id_found(self, mock_get):
        """Test getting incident type by ID when found."""
        mock_type = Mock(spec=models.IncidentType)
        mock_type.id = 1
        mock_type.name = "Test Type"
        mock_get.return_value = mock_type

        result = self.service.get_incident_type_by_id(self.mock_db, 1)

        assert result == mock_type
        mock_get.assert_called_once_with(self.mock_db, id=1)

    @patch('incident_api.crud.incident_type.get')
    def test_get_incident_type_by_id_not_found(self, mock_get):
        """Test getting incident type by ID when not found."""
        mock_get.return_value = None

        result = self.service.get_incident_type_by_id(self.mock_db, 999)

        assert result is None

    @patch('incident_api.crud.incident_type.get_multi')
    def test_get_all_incident_types(self, mock_get_multi):
        """Test getting all incident types."""
        mock_types = [Mock(spec=models.IncidentType) for _ in range(3)]
        mock_get_multi.return_value = mock_types

        result = self.service.get_all_incident_types(self.mock_db, skip=0, limit=10)

        assert result == mock_types
        mock_get_multi.assert_called_once_with(self.mock_db, skip=0, limit=10)

    @patch('incident_api.crud.incident_type.create')
    def test_create_incident_type(self, mock_create):
        """Test creating an incident type."""
        type_data = schemas.IncidentTypeCreate(name="New Type", incident_category_id=1, description="Description")
        mock_created_type = Mock(spec=models.IncidentType)
        mock_create.return_value = mock_created_type

        result = self.service.create_incident_type(self.mock_db, type_data)

        assert result == mock_created_type
        mock_create.assert_called_once_with(self.mock_db, obj_in=type_data)


class TestAttackVectorService:
    """Test AttackVectorService methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AttackVectorService()
        self.mock_db = Mock(spec=Session)

    @patch('incident_api.crud.attack_vector.get')
    def test_get_attack_vector_by_id_found(self, mock_get):
        """Test getting attack vector by ID when found."""
        mock_vector = Mock(spec=models.AttackVector)
        mock_vector.id = 1
        mock_vector.name = "Test Vector"
        mock_get.return_value = mock_vector

        result = self.service.get_attack_vector_by_id(self.mock_db, 1)

        assert result == mock_vector
        mock_get.assert_called_once_with(self.mock_db, id=1)

    @patch('incident_api.crud.attack_vector.get')
    def test_get_attack_vector_by_id_not_found(self, mock_get):
        """Test getting attack vector by ID when not found."""
        mock_get.return_value = None

        result = self.service.get_attack_vector_by_id(self.mock_db, 999)

        assert result is None

    @patch('incident_api.crud.attack_vector.get_multi')
    def test_get_all_attack_vectors(self, mock_get_multi):
        """Test getting all attack vectors."""
        mock_vectors = [Mock(spec=models.AttackVector) for _ in range(3)]
        mock_get_multi.return_value = mock_vectors

        result = self.service.get_all_attack_vectors(self.mock_db, skip=0, limit=10)

        assert result == mock_vectors
        mock_get_multi.assert_called_once_with(self.mock_db, skip=0, limit=10)

    @patch('incident_api.crud.attack_vector.create')
    def test_create_attack_vector(self, mock_create):
        """Test creating an attack vector."""
        vector_data = schemas.AttackVectorCreate(name="New Vector", description="Description")
        mock_created_vector = Mock(spec=models.AttackVector)
        mock_create.return_value = mock_created_vector

        result = self.service.create_attack_vector(self.mock_db, vector_data)

        assert result == mock_created_vector
        mock_create.assert_called_once_with(self.mock_db, obj_in=vector_data)