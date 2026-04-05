import pytest
import httpx

BASE_URL = "https://jsonplaceholder.typicode.com"

# One function covers 5 scenarios
@pytest.mark.parametrize("post_id, expected_status", [
    (1,     200),  # valid post
    (50,    200),  # valid post, middle range
    (100,   200),  # last valid post
    (101,   404),  # just over the limit
    (99999, 404),  # way out of range
])
def test_get_post_status(api_client, post_id, expected_status):
    response = api_client.get(f"{BASE_URL}/posts/{post_id}")
    assert response.status_code == expected_status
  
# Parameterize with schema validation
@pytest.mark.parametrize("post_id", [1, 25, 50, 75, 100])
def test_post_schema_is_consistent(api_client, post_id):
    response = api_client.get(f"{BASE_URL}/posts/{post_id}")
    data = response.json()

    assert isinstance(data["id"], int)
    assert isinstance(data["userId"], int)
    assert isinstance(data["title"], str)
    assert len(data["title"]) > 0      # title is never empty
    assert isinstance(data["body"], str)
    assert data["id"] == post_id       # id matches what we requested

#One more — parametrize POST with different payloads:
@pytest.mark.parametrize("payload, expected_status", [
    ({"title": "valid", "body": "content", "userId": 1}, 201),  # happy path
    ({"title": "no body",                 "userId": 1}, 201),  # missing body field
    ({"title": "no userId", "body": "x"              }, 201),  # missing userId
    ({},                                               201),  # empty payload
])
def test_create_post_variations(api_client, payload, expected_status):
    response = api_client.post(f"{BASE_URL}/posts", json=payload)
    assert response.status_code == expected_status