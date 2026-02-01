"""Test configuration and fixtures for the FastAPI app."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Save original state
    from app import activities as app_activities
    original_state = {
        key: {
            **value,
            "participants": value["participants"].copy()
        }
        for key, value in app_activities.items()
    }
    
    yield
    
    # Restore original state after test
    app_activities.clear()
    app_activities.update(original_state)
