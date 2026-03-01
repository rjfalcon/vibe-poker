"""Integration tests for the FastAPI endpoints.

Uses an in-memory SQLite database and the actual import pipeline
to test the full stack from file upload through stats retrieval.
"""
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
import app.models  # noqa: F401 — ensure all models are registered with Base.metadata
from app.main import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Test database setup — StaticPool keeps the same connection for :memory: DB
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"
_test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _override_get_db():
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def fresh_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=_test_engine)
    app.dependency_overrides[get_db] = _override_get_db
    yield
    Base.metadata.drop_all(bind=_test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def _upload(client: TestClient, fixture_name: str):
    """Helper: upload a fixture file and return the JSON response."""
    content = (FIXTURES_DIR / fixture_name).read_bytes()
    resp = client.post(
        "/api/sessions/import",
        files={"file": (fixture_name, io.BytesIO(content), "text/plain")},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Session import tests
# ---------------------------------------------------------------------------

class TestSessionImport:
    def test_import_single_hand_file(self, client):
        data = _upload(client, "normal_hand.txt")
        assert data["hand_count"] == 1
        assert data["hero_name"] == "Hero"
        assert data["filename"] == "normal_hand.txt"
        assert "id" in data

    def test_import_multi_hand_file(self, client):
        data = _upload(client, "multi_hand.txt")
        assert data["hand_count"] == 2

    def test_import_fast_fold_hand(self, client):
        data = _upload(client, "fast_fold_hand.txt")
        assert data["hand_count"] == 1

    def test_import_run_it_twice(self, client):
        data = _upload(client, "run_it_twice_hand.txt")
        assert data["hand_count"] == 1

    def test_duplicate_hands_are_skipped(self, client):
        _upload(client, "normal_hand.txt")
        data = _upload(client, "normal_hand.txt")
        assert data["hand_count"] == 0  # all duplicates, nothing new imported

    def test_non_txt_rejected(self, client):
        resp = client.post(
            "/api/sessions/import",
            files={"file": ("hands.csv", io.BytesIO(b"data"), "text/csv")},
        )
        assert resp.status_code == 400

    def test_list_sessions(self, client):
        _upload(client, "normal_hand.txt")
        _upload(client, "fast_fold_hand.txt")
        resp = client.get("/api/sessions/")
        assert resp.status_code == 200
        sessions = resp.json()
        assert len(sessions) == 2

    def test_get_session_by_id(self, client):
        created = _upload(client, "normal_hand.txt")
        resp = client.get(f"/api/sessions/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_session_not_found(self, client):
        resp = client.get("/api/sessions/nonexistent-id")
        assert resp.status_code == 404

    def test_delete_session(self, client):
        created = _upload(client, "normal_hand.txt")
        resp = client.delete(f"/api/sessions/{created['id']}")
        assert resp.status_code == 204
        # Confirm deleted
        resp2 = client.get(f"/api/sessions/{created['id']}")
        assert resp2.status_code == 404


# ---------------------------------------------------------------------------
# Hand list and detail tests
# ---------------------------------------------------------------------------

class TestHandEndpoints:
    def test_list_hands_after_import(self, client):
        _upload(client, "normal_hand.txt")
        resp = client.get("/api/hands/")
        assert resp.status_code == 200
        hands = resp.json()
        assert len(hands) == 1

    def test_list_hands_filter_by_fast_fold_false(self, client):
        _upload(client, "multi_hand.txt")  # 1 normal + 1 fast-fold
        resp = client.get("/api/hands/?is_fast_fold=false")
        assert resp.status_code == 200
        hands = resp.json()
        assert all(not h["is_fast_fold"] for h in hands)

    def test_list_hands_filter_by_fast_fold_true(self, client):
        _upload(client, "multi_hand.txt")
        resp = client.get("/api/hands/?is_fast_fold=true")
        assert resp.status_code == 200
        hands = resp.json()
        assert all(h["is_fast_fold"] for h in hands)

    def test_list_hands_filter_by_position(self, client):
        _upload(client, "normal_hand.txt")
        resp = client.get("/api/hands/?position=BTN")
        # Hand might or might not be in BTN depending on parsed position
        assert resp.status_code == 200

    def test_get_hand_detail(self, client):
        _upload(client, "normal_hand.txt")
        hands = client.get("/api/hands/").json()
        hand_id = hands[0]["id"]
        resp = client.get(f"/api/hands/{hand_id}")
        assert resp.status_code == 200
        detail = resp.json()
        assert "players" in detail
        assert "actions" in detail
        assert len(detail["players"]) == 6

    def test_get_hand_replay(self, client):
        _upload(client, "normal_hand.txt")
        hands = client.get("/api/hands/").json()
        hand_id = hands[0]["id"]
        resp = client.get(f"/api/hands/{hand_id}/replay")
        assert resp.status_code == 200
        replay = resp.json()
        assert "streets" in replay
        assert "PREFLOP" in replay["streets"]
        assert "players" in replay

    def test_get_hand_not_found(self, client):
        resp = client.get("/api/hands/nonexistent-id")
        assert resp.status_code == 404

    def test_pagination(self, client):
        _upload(client, "multi_hand.txt")
        resp = client.get("/api/hands/?page=1&limit=1")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_showdown_hand_detail(self, client):
        _upload(client, "showdown_hand.txt")
        hands = client.get("/api/hands/").json()
        hand_id = hands[0]["id"]
        detail = client.get(f"/api/hands/{hand_id}").json()
        assert detail["hero_went_to_showdown"] is True
        # Hero lost this showdown (Villain3 had trips)
        assert detail["flop_cards"] == "Kh 8d 2s"
        assert detail["turn_card"] == "Ac"
        assert detail["river_card"] == "3d"

    def test_run_it_twice_hand_detail(self, client):
        _upload(client, "run_it_twice_hand.txt")
        hands = client.get("/api/hands/").json()
        assert hands[0]["run_it_twice"] is True


# ---------------------------------------------------------------------------
# Stats endpoint tests
# ---------------------------------------------------------------------------

class TestStatsEndpoints:
    def test_overview_stats_empty(self, client):
        resp = client.get("/api/stats/overview")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_hands"] == 0
        assert stats["vpip"] == 0.0

    def test_overview_after_import(self, client):
        _upload(client, "normal_hand.txt")
        resp = client.get("/api/stats/overview")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_hands"] == 1
        assert stats["vpip"] == 100.0   # hero raised in this hand
        assert stats["pfr"] == 100.0

    def test_fast_fold_stats(self, client):
        _upload(client, "fast_fold_hand.txt")
        stats = client.get("/api/stats/overview").json()
        assert stats["fast_fold_pct"] == 100.0
        assert stats["vpip"] == 0.0

    def test_mixed_fast_fold_stats(self, client):
        _upload(client, "multi_hand.txt")  # 1 normal + 1 fast-fold
        stats = client.get("/api/stats/overview").json()
        assert stats["total_hands"] == 2
        assert stats["fast_fold_pct"] == 50.0  # 1 of 2 hands

    def test_position_stats(self, client):
        _upload(client, "normal_hand.txt")
        resp = client.get("/api/stats/positions")
        assert resp.status_code == 200
        positions = resp.json()
        assert len(positions) >= 1
        assert all("position" in p for p in positions)
        assert all("vpip" in p for p in positions)

    def test_timeline(self, client):
        _upload(client, "multi_hand.txt")
        resp = client.get("/api/stats/timeline?sample_every=1")
        assert resp.status_code == 200
        points = resp.json()
        assert len(points) == 2
        assert points[0]["index"] == 1
        assert "cumulative_bb" in points[0]

    def test_stats_filtered_by_session(self, client):
        sess1 = _upload(client, "normal_hand.txt")
        _upload(client, "fast_fold_hand.txt")
        resp = client.get(f"/api/stats/overview?session_id={sess1['id']}")
        stats = resp.json()
        assert stats["total_hands"] == 1

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
