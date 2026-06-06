import pytest
import json
from unittest.mock import patch, MagicMock
import server
from server import mcp, CROSSWALK_DATA, REPORTING_CLOCKS_DATA

@pytest.fixture(autouse=True)
def mock_auth():
    with patch('server._shared_check_access') as mock:
        mock.return_value = (True, "OK", "pro")
        yield mock

@pytest.fixture(autouse=True)
def reset_usage():
    server._usage = {}
    yield

class TestDORANIS2Crosswalk:
    def test_list_overlapping_obligations(self):
        result = server.list_overlapping_obligations(api_key="test_key")
        assert result.overlap_percent_estimate == 65
        assert len(result.crosswalk) == len(CROSSWALK_DATA)
        assert result.branding == "Built by MEOK AI Labs | https://meok.ai"

    def test_compare_reporting_clocks(self):
        result = server.compare_reporting_clocks(api_key="test_key")
        assert "DORA" in result.reporting_clocks
        assert "NIS2" in result.reporting_clocks
        assert "SLA" in result.practical_implication

    def test_check_dual_compliance_full_pass(self):
        # Provide specific keywords that match the satisfies_both_if fields
        controls = [
            "board-signed", "reviewed annually", "senior accountable person", # Art 5
            "ict risk register", "critical-or-important function", "flags controls", # Art 6-16
            "2024/1772 classification", "competent-authority notification", # Art 17
            "dora major flag", "nis2 significant flag", # Art 18
            "triggers both clocks", "parallel", # Art 19
            "tlpt scope", "pen-test programme", # Art 24-27
            "source of truth", "supplier data", # Art 28-30
            "member of a shared forum", "national csirt" # Art 45
        ]
        controls_csv = ", ".join(controls)
        result = server.check_dual_compliance(entity_name="Test Bank", controls_csv=controls_csv, api_key="test_key")
        assert result.overall_dual_compliance_percent == 100.0
        assert result.entity == "Test Bank"
        assert all(obl.state == "PASS" for obl in result.obligations)

    def test_check_dual_compliance_gap(self):
        result = server.check_dual_compliance(entity_name="Test Bank", controls_csv="", api_key="test_key")
        assert result.overall_dual_compliance_percent == 0
        assert all(obl.state == "GAP" for obl in result.obligations)

    def test_sign_attestation_pro_tier(self):
        with patch('server._attestation') as mock_attest:
            mock_attest.return_value = {"status": "success", "certificate_id": "123"}
            result = server.sign_dual_compliance_attestation(entity_name="Test Bank", overall_score=85.0, api_key="test_key")
            assert result["status"] == "success"

    def test_rate_limiting_pro_tier(self):
        # Pro tier should not be rate limited
        for _ in range(20):
            assert server._rl("pro") is None

    def test_rate_limiting_free_tier(self):
        server._usage["anonymous"] = []
        for _ in range(10):
            assert server._rl("free") is None
        assert "Free tier limit" in server._rl("free")

    def test_obligation_detail_model(self):
        from server import ObligationDetail
        data = CROSSWALK_DATA["DORA Art 5 — Governance & organisation"]
        obj = ObligationDetail(**data)
        assert obj.nis2_equivalent.startswith("NIS2 Art 20")

    def test_check_dual_compliance_partial(self):
        # Match only 1 keyword for some, 0 for others
        controls = "board-signed, ict risk register, incident-response runbook"
        result = server.check_dual_compliance(entity_name="Test Bank", controls_csv=controls, api_key="test_key")
        assert 0 < result.overall_dual_compliance_percent < 100.0
        # Check that we have some PARTIAL and some GAP
        states = [obl.state for obl in result.obligations]
        assert "PARTIAL" in states
        assert "GAP" in states

    def test_reporting_clock_detail_model(self):
        from server import ReportingClockDetail
        data = REPORTING_CLOCKS_DATA["DORA"]
        obj = ReportingClockDetail(**data)
        assert obj.initial == "4 hours from classification"
