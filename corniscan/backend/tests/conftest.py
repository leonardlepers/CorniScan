"""Fixtures partagées pour les tests CorniScan."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Client de test FastAPI."""
    return TestClient(app)
