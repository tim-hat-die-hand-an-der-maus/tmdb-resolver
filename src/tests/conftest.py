import pytest
from fastapi.testclient import TestClient

from tmdb_resolver.api import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
