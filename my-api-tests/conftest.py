# conftest.py
import pytest
import httpx

@pytest.fixture(scope="session")
def api_client():
    with httpx.Client(base_url="https://jsonplaceholder.typicode.com") as client:
        yield client