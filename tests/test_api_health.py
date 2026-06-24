from fastapi.testclient import TestClient

from app.api.main import create_app
from app.core.config import Settings


def test_health_endpoint() -> None:
    app = create_app(Settings(app_env="test"))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "test"}
