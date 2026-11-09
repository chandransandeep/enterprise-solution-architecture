import os
os.environ["DATABASE_URL"] = "sqlite:///./test_civic_talent.db"
os.environ["API_KEY"] = "test-only-key"

from fastapi.testclient import TestClient
from app.main import app, engine
from app.models import Base


def test_recruitment_workflow():
    Base.metadata.drop_all(engine)
    with TestClient(app) as client:
        assert client.get("/health/ready").status_code == 200
        assert client.get("/v1/candidates").status_code == 401
        h = {"X-API-Key": "test-only-key"}
        candidate = client.post("/v1/candidates", headers=h, json={"name": "Example Person", "email": "example@example.com", "skills": ["SQL"]})
        assert candidate.status_code == 201
        assert client.post("/v1/candidates", headers=h, json={"name": "Example Person", "email": "example@example.com"}).status_code == 409
        vacancy = client.post("/v1/vacancies", headers=h, json={"title": "Architect", "department": "Technology"})
        assert vacancy.status_code == 201
        application = client.post("/v1/applications", headers=h, json={"candidate_id": candidate.json()["id"], "vacancy_id": vacancy.json()["id"]})
        assert application.status_code == 201
        identifier = application.json()["id"]
        assert client.patch(f"/v1/applications/{identifier}/status", headers=h, json={"status": "offered"}).status_code == 409
        for phase in ("reviewing", "interview", "offered"):
            result = client.patch(f"/v1/applications/{identifier}/status", headers=h, json={"status": phase})
            assert result.status_code == 200
            assert result.json()["status"] == phase
        assert client.get("/v1/candidates", headers=h).json()[0]["name"] == "Example Person"
    Base.metadata.drop_all(engine)
