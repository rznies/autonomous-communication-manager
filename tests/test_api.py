"""Tests for the FastAPI server (api.py)."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Provide a fresh TestClient for each test."""
    from emailmanagement.api import app

    return TestClient(app)


# ---------------------------------------------------------------------------
# Skeleton / infra
# ---------------------------------------------------------------------------
def test_app_is_importable():
    from emailmanagement.api import app

    assert app is not None


def test_app_has_cors_headers(client):
    response = client.options(
        "/api/metrics",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_docs_endpoint_returns_html(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# GET /api/metrics
# ---------------------------------------------------------------------------
def test_metrics_returns_valid_json(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "idrr_score" in data
    assert "correction_rate" in data
    assert "handled_total" in data
    assert "total_incoming" in data
    assert "total_automated" in data
    assert "total_corrections" in data
    assert isinstance(data["idrr_score"], (int, float))
    assert isinstance(data["handled_total"], int)


# ---------------------------------------------------------------------------
# GET /api/queue  +  POST /api/queue/{id}/approve
# ---------------------------------------------------------------------------
def test_queue_returns_list(client):
    response = client.get("/api/queue")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_queue_item_has_required_fields(client):
    data = client.get("/api/queue").json()
    item = data[0]
    assert "id" in item
    assert "type" in item
    assert "recipient" in item
    assert "title" in item
    assert "score" in item
    assert "one_line_summary" in item


def test_approve_returns_success(client):
    response = client.post("/api/queue/1/approve")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_approve_removes_item_from_queue(client):
    client.post("/api/queue/2/approve")
    ids = [item["id"] for item in client.get("/api/queue").json()]
    assert 2 not in ids


def test_approve_nonexistent_returns_404(client):
    response = client.post("/api/queue/9999/approve")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/contacts
# ---------------------------------------------------------------------------
def test_contacts_returns_list(client):
    response = client.get("/api/contacts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_contact_has_required_fields(client):
    data = client.get("/api/contacts").json()
    contact = data[0]
    assert "id" in contact
    assert "relationship_class" in contact
    assert "importance_score" in contact
    assert "interaction_count" in contact
    assert "is_protected" in contact


def test_contacts_sorted_by_importance_descending(client):
    data = client.get("/api/contacts").json()
    scores = [c["importance_score"] for c in data]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# GET /api/activity
# ---------------------------------------------------------------------------
def test_activity_returns_list(client):
    response = client.get("/api/activity")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_activity_item_has_required_fields(client):
    data = client.get("/api/activity").json()
    action = data[0]
    assert "id" in action
    assert "decision" in action
    assert "reason" in action
    assert "timestamp" in action
    assert "is_reversible" in action
