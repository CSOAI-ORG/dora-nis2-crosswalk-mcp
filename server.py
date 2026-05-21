#!/usr/bin/env python3
"""
DORA × NIS2 Crosswalk Compliance MCP Server
=============================================
By MEOK AI Labs | https://meok.ai

The only MCP server that maps Regulation (EU) 2022/2554 (DORA) obligations to
Directive (EU) 2022/2555 (NIS2) Article 21 & 23 measures, and vice versa —
so you can prove dual compliance without re-auditing the same controls twice.

TARGET: EU banks, insurers, asset managers, payment institutions, crypto-asset
service providers, and their critical ICT third-party service providers (CTPPs).
Most are in scope for BOTH regimes. The obligations overlap ~60-70% — but the
reporting channels, deadlines, and sanctions differ.

DOMAIN BENEFIT: a single Register-of-Information dataset + a single incident-
classification workflow can satisfy both DORA Article 17-23 AND NIS2 Article
21-23 — if you map them correctly. This MCP does the mapping.

Install: pip install dora-nis2-crosswalk-mcp
Run:     python server.py
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

import os as _os
import sys
import os

_MEOK_API_KEY = _os.environ.get("MEOK_API_KEY", "")

try:
    from auth_middleware import check_access as _shared_check_access
    _AUTH_ENGINE_AVAILABLE = True
except ImportError:
    _AUTH_ENGINE_AVAILABLE = False

    def _shared_check_access(api_key: str = ""):
        """Fallback when shared auth engine is not available."""
        if _MEOK_API_KEY and api_key and api_key == _MEOK_API_KEY:
            return True, "OK", "pro"
        if _MEOK_API_KEY and api_key and api_key != _MEOK_API_KEY:
            return False, "Invalid API key. Get one at https://meok.ai/api-keys", "free"
        return True, "OK", "free"


try:
    from attestation import get_attestation_tool_response
    _ATTESTATION_LOCAL = True
except ImportError:
    _ATTESTATION_LOCAL = False

_ATTESTATION_API = _os.environ.get(
    "MEOK_ATTESTATION_API", "https://meok-attestation-api.vercel.app"
)


def _sign_via_api(api_key, regulation, entity, score, findings, articles_audited, tier="pro", include_pdf_base64=False):
    import urllib.request as _url, urllib.error as _urlerr
    payload = {"api_key": api_key, "regulation": regulation, "entity": entity,
               "score": score, "findings": findings or [],
               "articles_audited": articles_audited or [], "tier": tier}
    try:
        req = _url.Request(f"{_ATTESTATION_API}/sign",
                           data=json.dumps(payload).encode("utf-8"),
                           headers={"Content-Type": "application/json"})
        with _url.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except _urlerr.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {"error": f"Attestation API HTTP {e.code}. Contact hello@meok.ai."}
    except Exception as e:
        return {"error": f"Could not reach MEOK attestation API: {e}."}


def _attestation(regulation, entity, score, findings, articles_audited, tier, include_pdf_base64, api_key):
    if _ATTESTATION_LOCAL:
        return get_attestation_tool_response(
            regulation=regulation, entity=entity, score=score, findings=findings,
            articles_audited=articles_audited, tier=tier, include_pdf_base64=include_pdf_base64,
        )
    return _sign_via_api(api_key=api_key, regulation=regulation, entity=entity,
                        score=score, findings=findings, articles_audited=articles_audited or [],
                        tier=tier, include_pdf_base64=include_pdf_base64)


def check_access(api_key: str = ""):
    return _shared_check_access(api_key)


FREE_DAILY_LIMIT = 10
_usage: dict[str, list[datetime]] = defaultdict(list)
STRIPE_199 = "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"
STRIPE_1499 = "https://buy.stripe.com/4gM9AV80kaEG0ZT42k8k837"
STRIPE_5K = "https://buy.stripe.com/4gM7sN2G0bIKeQJfL28k833"


def _rl(tier="free") -> Optional[str]:
    if tier in ("pro", "professional", "enterprise"):
        return None
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=1)
    _usage["anonymous"] = [t for t in _usage["anonymous"] if t > cutoff]
    if len(_usage["anonymous"]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit ({FREE_DAILY_LIMIT}/day). Pro £199/mo: {STRIPE_199}"
    _usage["anonymous"].append(now)
    return None


# ── DORA ↔ NIS2 Crosswalk ──────────────────────────────────────
# For each DORA obligation cluster, the equivalent NIS2 Article 21(2) measure.
# Mapping is based on: EBA/ESMA joint opinion on DORA-NIS2 interplay (2024),
# Commission DORA/NIS2 guidance, and practitioner consensus. NOT legal advice.

CROSSWALK = {
    "DORA Art 5 — Governance & organisation": {
        "nis2_equivalent": "NIS2 Art 20 — Governance + Art 21(2)(a) risk analysis policies",
        "shared_evidence": ["Board-approved ICT/security policy", "Named senior accountable person"],
        "dora_specific": "Explicit 'management body' sign-off + annual review",
        "nis2_specific": "Management body training attestation",
        "satisfies_both_if": "Policy is board-signed, reviewed annually, and the senior accountable person is named in both filings",
    },
    "DORA Art 6–16 — ICT risk management framework": {
        "nis2_equivalent": "NIS2 Art 21(2)(a) risk analysis + (b) incident handling + (c) business continuity + (d) supply-chain",
        "shared_evidence": ["ICT risk register", "Control catalogue", "Third-party risk assessments"],
        "dora_specific": "Detailed classification of ICT-supported business functions + criticality tiering (Art 8)",
        "nis2_specific": "Application to the 10 prescribed measures; crypto + MFA explicit",
        "satisfies_both_if": "The ICT risk register identifies each critical-or-important function AND flags controls against each Article 21(2) measure",
    },
    "DORA Art 17 — Incident process": {
        "nis2_equivalent": "NIS2 Art 21(2)(b) incident handling",
        "shared_evidence": ["Incident-response runbook", "Playbook for major incidents"],
        "dora_specific": "Classification criteria per Commission Delegated Regulation (EU) 2024/1772 (customers affected, duration, economic impact, data, cross-border, criticality)",
        "nis2_specific": "Same incident-handling capability but broader scope — any significant cyber threat or incident",
        "satisfies_both_if": "The runbook uses the 2024/1772 classification thresholds and invokes BOTH competent-authority notification paths",
    },
    "DORA Art 18 — Incident classification": {
        "nis2_equivalent": "NIS2 Art 23 — incident reporting (thresholds + classification)",
        "shared_evidence": ["Automated classification logic (your detection tool)", "Decision log when thresholds tripped"],
        "dora_specific": "'Major ICT incident' thresholds + 'significant cyber threat' separately",
        "nis2_specific": "'Significant incident' threshold (≥2 essential-entity sectoral thresholds) + ~24h early warning",
        "satisfies_both_if": "The classifier emits both a DORA major flag AND a NIS2 significant flag on a single incident, routing notifications to both channels",
    },
    "DORA Art 19 — Reporting to competent authority": {
        "nis2_equivalent": "NIS2 Art 23 — reporting",
        "shared_evidence": ["Incident notification template", "SLA clocks on notification"],
        "dora_specific": "Initial within 4 hours of classification as major → 72h intermediate → 1 month final",
        "nis2_specific": "24h early warning → 72h incident notification → 1 month final report → 3 months progress (if requested)",
        "satisfies_both_if": "Your notification workflow triggers BOTH clocks in parallel + emits to DORA competent authority (national FSA/BaFin/AMF/etc) AND NIS2 competent authority (CSIRT)",
    },
    "DORA Art 24–27 — Resilience testing + TLPT": {
        "nis2_equivalent": "NIS2 Art 21(2)(f) testing + (g) training",
        "shared_evidence": ["Annual pen-test programme", "Training log for staff"],
        "dora_specific": "TLPT (Threat-Led Penetration Testing) every 3y for significant entities; TIBER-EU methodology",
        "nis2_specific": "Effectiveness testing of the 10 Art 21(2) measures",
        "satisfies_both_if": "TLPT scope documents mention NIS2 measure coverage AND the internal pen-test programme schedule includes NIS2 measure-by-measure effectiveness",
    },
    "DORA Art 28–30 — ICT third-party risk": {
        "nis2_equivalent": "NIS2 Art 21(2)(d) supply-chain security",
        "shared_evidence": ["Register of Information (DORA)", "Vendor risk assessments", "Contractual clauses"],
        "dora_specific": "Register of Information required format (Commission Implementing Regulation (EU) 2024/2956); annual submission",
        "nis2_specific": "Risk-management of dependencies + supplier relationships",
        "satisfies_both_if": "The DORA Register of Information is the SINGLE source of truth for supplier data and also generates the NIS2 supply-chain dependencies view",
    },
    "DORA Art 45 — Information sharing": {
        "nis2_equivalent": "NIS2 Art 29 — voluntary information sharing",
        "shared_evidence": ["Membership of a recognised information-sharing arrangement"],
        "dora_specific": "Voluntary exchange of cyber-threat intelligence among financial entities",
        "nis2_specific": "Voluntary information-sharing + CSIRT cooperation",
        "satisfies_both_if": "Member of a shared forum (e.g. FS-ISAC Europe or national financial-sector ISAC + national CSIRT community)",
    },
}

REPORTING_CLOCKS = {
    "DORA": {
        "trigger": "Classification as 'major ICT incident' per (EU) 2024/1772",
        "initial": "4 hours from classification",
        "intermediate": "72 hours from classification",
        "final": "1 month from classification",
        "authority": "National financial competent authority (BaFin, AMF, Banca d'Italia, FCA/PRA during transitional period, etc.)",
    },
    "NIS2": {
        "trigger": "Classification as 'significant incident' per national transposition (typically: threshold on service disruption, financial loss, data compromise, or essential/important entity sectoral threshold)",
        "early_warning": "24 hours from awareness (indication of whether malicious / cross-border)",
        "incident_notification": "72 hours from awareness (initial assessment)",
        "final_report": "1 month from incident notification",
        "progress_report": "Up to 3 months if competent authority requests",
        "authority": "National CSIRT + competent authority (often BSI / ANSSI / ACN / NCSC-NL / DNSC)",
    },
}


mcp = FastMCP(
    "dora-nis2-crosswalk",
    instructions=(
        "MEOK AI Labs DORA × NIS2 Crosswalk MCP. Maps DORA (Regulation (EU) 2022/2554) "
        "obligations to NIS2 (Directive (EU) 2022/2555) Article 21-23 measures and vice versa. "
        "Primary use: banks + insurers + payment institutions + CTPPs in scope for both. "
        "Ask me to list overlapping obligations, check dual compliance, compare reporting "
        "clocks, or issue a signed dual-compliance attestation."
    ),
)


@mcp.tool()
def list_overlapping_obligations(api_key: str = "") -> str:
    """Return the full DORA → NIS2 crosswalk table with shared evidence + regime-specific
    requirements + 'satisfies both if' test."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if err := _rl(tier):
        return json.dumps({"error": err, "upgrade_url": STRIPE_199})
    return json.dumps({
        "legal_basis": "DORA = Regulation (EU) 2022/2554 | NIS2 = Directive (EU) 2022/2555",
        "crosswalk": CROSSWALK,
        "overlap_percent_estimate": 65,
        "disclaimer": "Estimate based on EBA/ESMA joint opinion + practitioner consensus 2024. Not legal advice.",
        "upsell_pro": f"Pro £199/mo unlocks dual-compliance gap analysis + signed attestations: {STRIPE_199}" if tier == "free" else None,
    }, indent=2)


@mcp.tool()
def compare_reporting_clocks(api_key: str = "") -> str:
    """Show side-by-side DORA vs NIS2 incident-reporting clocks."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    return json.dumps({
        "reporting_clocks": REPORTING_CLOCKS,
        "practical_implication": (
            "If you are in scope for BOTH and a single ICT incident meets BOTH classification "
            "thresholds, you must notify BOTH authorities in parallel. The NIS2 24h early warning "
            "is the tightest SLA — design detection + escalation to that clock."
        ),
    }, indent=2)


@mcp.tool()
def check_dual_compliance(
    entity_name: str,
    controls_csv: str,
    api_key: str = "",
) -> str:
    """Score dual DORA + NIS2 compliance given a comma-separated list of current controls.

    Each crosswalk row is scored PASS / PARTIAL / GAP based on how many 'satisfies-both'
    test keywords match the controls list.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if err := _rl(tier):
        return json.dumps({"error": err, "upgrade_url": STRIPE_199})

    controls = [c.strip().lower() for c in controls_csv.split(",") if c.strip()]
    results = []
    passes = 0
    for obligation, detail in CROSSWALK.items():
        satisfies = detail["satisfies_both_if"].lower()
        # naïve keyword score — count how many controls are mentioned in the satisfies test
        matches = [c for c in controls if c in satisfies or any(w in satisfies for w in c.split())]
        if len(matches) >= 2:
            state, score = "PASS", 1.0
            passes += 1
        elif matches:
            state, score = "PARTIAL", 0.5
            passes += 0.5
        else:
            state, score = "GAP", 0.0
        results.append({
            "obligation": obligation,
            "nis2_equivalent": detail["nis2_equivalent"],
            "state": state,
            "satisfies_both_if": detail["satisfies_both_if"],
            "matched_controls": matches,
        })

    overall_score = round(100 * passes / len(CROSSWALK), 1)
    return json.dumps({
        "entity": entity_name,
        "overall_dual_compliance_percent": overall_score,
        "obligations": results,
        "upsell_pro": f"Pro £199/mo: signed dual-compliance attestation + gap-remediation plan: {STRIPE_199}" if tier == "free" else None,
    }, indent=2)


@mcp.tool()
def sign_dual_compliance_attestation(
    entity_name: str,
    overall_score: float,
    findings_csv: str = "",
    include_pdf_base64: bool = False,
    api_key: str = "",
) -> str:
    """Generate a cryptographically signed DORA × NIS2 dual-compliance attestation (Pro+)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if tier == "free":
        return json.dumps({
            "error": "Signed attestations require Pro (£199/mo) or Enterprise tier.",
            "upgrade_url": STRIPE_199,
            "why_pro": "Board-ready dual-compliance evidence for EU banks and financial entities.",
        })
    findings = [f.strip() for f in findings_csv.split(",") if f.strip()]
    cert = _attestation(
        regulation="DORA × NIS2 dual compliance (Regulation (EU) 2022/2554 + Directive (EU) 2022/2555)",
        entity=entity_name,
        score=overall_score,
        findings=findings or [f"Overall dual-compliance score: {overall_score}"],
        articles_audited=list(CROSSWALK.keys()),
        tier=tier,
        include_pdf_base64=include_pdf_base64,
        api_key=api_key,
    )
    return json.dumps(cert, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
