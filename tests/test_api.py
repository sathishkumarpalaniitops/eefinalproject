import sys
import os

# ✅ Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

# ✅ Mock data (simulating GitHub API response)
mock_github_response = [
    {
        "id": "1",
        "description": "Test gist",
        "html_url": "https://gist.github.com/test/1",
        "files": {"file1.txt": {}}
    }
]


# ✅ Positive test (mocked GitHub API)
@patch("app.main.httpx.AsyncClient.get")
def test_get_gists_mock(mock_get):
    class MockResponse:
        status_code = 200

        def json(self):
            return mock_github_response

    mock_get.return_value = MockResponse()

    response = client.get("/testuser")

    assert response.status_code == 200
    data = response.json()

    assert "gists" in data
    assert isinstance(data["gists"], list)
    assert data["gists"][0]["id"] == "1"
    assert data["gists"][0]["description"] == "Test gist"


# ✅ Negative test (user not found)
@patch("app.main.httpx.AsyncClient.get")
def test_user_not_found(mock_get):
    class MockResponse:
        status_code = 404

    mock_get.return_value = MockResponse()

    response = client.get("/unknownuser")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"