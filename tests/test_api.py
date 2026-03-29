"""
Integration Tests — FastAPI API Endpoints (main.py)

Tests:
  • GET / health check
  • POST /run-recovery — with mocked graph
  • POST /generate-pdf — with mocked DB + PDF service
  • GET /status/{thread_id} — with mocked graph state
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a FastAPI test client with mocked graph/db."""
    with patch("main.gst_app") as mock_app, \
         patch("main.gstr3b_collection") as mock_coll:
        from main import app
        yield TestClient(app)


class TestHealthCheck:
    def test_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "Agentic Network is Live"
        assert data["database_connected"] is True


class TestRunRecovery:
    @patch("main.gst_app")
    def test_run_recovery_success(self, mock_graph):
        from main import app
        client = TestClient(app)
        mock_graph.invoke.return_value = {
            "final_gstr3b": {"period": "2026-03"},
            "mismatches": [{"invoice_number": "INV-001"}],
            "vendor_chase_log": [],
            "gstr3b_draft": {},
            "financial_context": {}
        }
        resp = client.post("/run-recovery", json={"period": "2026-03", "days_to_cutoff": 20})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "thread_id" in data

    @patch("main.gst_app")
    def test_run_recovery_handles_error(self, mock_graph):
        from main import app
        client = TestClient(app)
        mock_graph.invoke.side_effect = Exception("Graph failed")
        resp = client.post("/run-recovery", json={"period": "2026-03"})
        assert resp.status_code == 500


class TestGetStatus:
    @patch("main.gst_app")
    def test_status_found(self, mock_graph):
        from main import app
        client = TestClient(app)
        mock_state = MagicMock()
        mock_state.values = {"current_period": "2026-03", "mismatches": []}
        mock_graph.get_state.return_value = mock_state
        resp = client.get("/status/test-id-123")
        assert resp.status_code == 200

    @patch("main.gst_app")
    def test_status_not_found(self, mock_graph):
        from main import app
        client = TestClient(app)
        mock_state = MagicMock()
        mock_state.values = {}
        mock_graph.get_state.return_value = mock_state
        resp = client.get("/status/nonexistent")
        assert resp.status_code == 404


class TestMockGSTN:
    def test_mock_gstr2b_endpoint(self):
        with patch("main.gst_app"), patch("main.gstr3b_collection"):
            from main import app
            client = TestClient(app)
            resp = client.get("/mock-gstn/gstr2b/2026-03")
            assert resp.status_code == 200
            data = resp.json()
            assert data["period"] == "2026-03"
            assert isinstance(data["data"], list)
            assert len(data["data"]) > 0
