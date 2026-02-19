from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# -------------------------
# BASIC ENDPOINT TESTS
# -------------------------

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200


def test_valid_crm_request():
    response = client.get("/data?source=crm")
    assert response.status_code == 200

    body = response.json()
    assert body["source"] == "crm"
    assert "data" in body
    assert "metadata" in body


def test_valid_support_filter():
    response = client.get("/data?source=support&status=open")
    assert response.status_code == 200


def test_source_is_case_insensitive():
    response = client.get("/data?source=Support&status=open")
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "support"


def test_valid_crm_status_filter():
    response = client.get("/data?source=crm&status=active")
    assert response.status_code == 200

    body = response.json()
    assert body["source"] == "crm"
    for row in body["data"]:
        assert row["status"] == "active"


def test_valid_analytics_filter():
    response = client.get("/data?source=analytics&metric=daily_active_users")
    assert response.status_code == 200


# -------------------------
# INVALID FILTER TESTS
# -------------------------

def test_invalid_filter_for_crm():
    response = client.get("/data?source=crm&priority=high")
    assert response.status_code == 400


def test_invalid_filter_for_analytics():
    response = client.get("/data?source=analytics&status=open")
    assert response.status_code == 400


# -------------------------
# INVALID SORT FIELD
# -------------------------

def test_invalid_sort_field():
    response = client.get("/data?source=crm&sort_by=priority")
    assert response.status_code == 400


# -------------------------
# VALID SORT
# -------------------------

def test_valid_sort():
    response = client.get("/data?source=support&sort_by=created_at")
    assert response.status_code == 200


# -------------------------
# PAGINATION
# -------------------------

def test_pagination():
    response = client.get("/data?source=support&page=1&page_size=5")
    assert response.status_code == 200

    body = response.json()
    assert body["metadata"]["page_size"] == 5


def test_voice_mode_caps_page_size():
    # voice_mode=true (default) caps to DEFAULT_PAGE_SIZE=10
    response = client.get("/data?source=support&page=1&page_size=50")
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["page_size"] == 10

    # voice_mode=false allows larger page sizes (up to MAX_PAGE_SIZE)
    response = client.get("/data?source=support&page=1&page_size=50&voice_mode=false")
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["page_size"] == 50


# -------------------------
# SUMMARIZATION
# -------------------------

def test_summarize_true():
    response = client.get("/data?source=support&summarize=true")
    assert response.status_code == 200

    body = response.json()
    assert isinstance(body["data"], list)
    if body["data"]:
        # Voice summary should keep identity + actionability fields
        first = body["data"][0]
        assert "ticket_id" in first
        assert "subject" in first
        assert "priority" in first
        assert "status" in first


# -------------------------
# INVALID SOURCE
# -------------------------

def test_invalid_source():
    response = client.get("/data?source=invalid")
    assert response.status_code in [400, 422]

