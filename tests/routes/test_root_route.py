import pytest
from fastapi.testclient import TestClient

@pytest.mark.usefixtures("client")
class TestRootRoute:

    def test_read_root_success(self, client: TestClient):
        # Arrange
        expected_message = {"message": "Welcome to Internship Demo API!"}

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        assert response.json() == expected_message
