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

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import os as _os
import sys
import os

# --- Pydantic Models for Structured Output ---

class ObligationDetail(BaseModel):
    nis2_equivalent: str
    shared_evidence: List[str]
    dora_specific: str
    nis2_specific: str
    satisfies_both_if: str

class CrosswalkResponse(BaseModel):
    legal_basis: str
    crosswalk: Dict[str, ObligationDetail]
    overlap_percent_estimate: int
    disclaimer: str
    upsell_pro: Optional[str] = None
    branding: str = "Built by MEOK AI Labs | https://meok.ai"

class ReportingClockDetail(BaseModel):
    trigger: str
    initial: Optional[str] = None
    early_warning: Optional[str] = None
    incident_notification: Optional[str] = None
    intermediate: Optional[str] = None
    final: Optional[str] = None
    final_report: Optional[str] = None
    progress_report: Optional[str] = None
    authority: str

class ClocksResponse(BaseModel):
    reporting_clocks: Dict[str, ReportingClockDetail]
    practical_implication: str
    branding: str = "Built by MEOK AI Labs | https://meok.ai"

class ComplianceObligationResult(BaseModel):
    obligation: str
    nis2_equivalent: str
    state: str
    satisfies_both_if: str
    matched_controls: List[str]

class ComplianceResponse(BaseModel):
    entity: str
    overall_dual_compliance_percent: float
    obligations: List[ComplianceObligationResult]
    upsell_pro: Optional[str] = None
    branding: str = "Built by MEOK AI Labs | https://meok.ai"

# --- Constants & Data ---

CROSSWALK_DATA = {
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

REPORTING_CLOCKS_DATA = {
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

# --- Utils ---

_MEOK_API_KEY = _os.environ.get("MEOK_API_KEY", "")

try:
    from auth_middleware import check_access as _shared_check_access
    _AUTH_ENGINE_AVAILABLE = True
except ImportError:
    _AUTH_ENGINE_AVAILABLE = False
    def _shared_check_access(api_key: str = ""):
        if _MEOK_API_KEY and api_key and api_key == _MEOK_API_KEY:
            return True, "OK", "pro"
        return True, "OK, Pro at https://www.csoai.org/checkout", "free"

try:
    from attestation import get_attestation_tool_response
    _ATTESTATION_LOCAL = True
except ImportError:
    _ATTESTATION_LOCAL = False

_ATTESTATION_API = _os.environ.get("MEOK_ATTESTATION_API", "https://meok-attestation-api.vercel.app")

def _sign_via_api(api_key, regulation, entity, score, findings, articles_audited, tier="pro", include_pdf_base64=False):
    import urllib.request as _url, urllib.error as _urlerr
    payload = {"api_key": api_key, "regulation": regulation, "entity": entity, "score": score, "findings": findings or [], "articles_audited": articles_audited or [], "tier": tier}
    try:
        req = _url.Request(f"{_ATTESTATION_API}/sign", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with _url.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except _urlerr.HTTPError as e:
        try: return json.loads(e.read())
        except: return {"error": f"Attestation API HTTP {e.code}"}
    except Exception as e:
        return {"error": str(e)}

def _attestation(regulation, entity, score, findings, articles_audited, tier, include_pdf_base64, api_key):
    if _ATTESTATION_LOCAL:
        return get_attestation_tool_response(regulation=regulation, entity=entity, score=score, findings=findings, articles_audited=articles_audited, tier=tier, include_pdf_base64=include_pdf_base64)
    return _sign_via_api(api_key=api_key, regulation=regulation, entity=entity, score=score, findings=findings, articles_audited=articles_audited or [], tier=tier, include_pdf_base64=include_pdf_base64)

FREE_DAILY_LIMIT = 50
_usage = defaultdict(list)
STRIPE_199 = "https://buy.stripe.com/aFa7sNcgAdQS0ZT1Uc8k91t"

def _rl(tier="free"):
    if tier in ("pro", "professional", "enterprise"): return None
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=1)
    _usage["anonymous"] = [t for t in _usage["anonymous"] if t > cutoff]
    if len(_usage["anonymous"]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit ({FREE_DAILY_LIMIT}/day). Pro £199/mo: {STRIPE_199}"
    _usage["anonymous"].append(now)
    return None

# --- MCP Setup ---

mcp = FastMCP(
    "dora-nis2-crosswalk",
    instructions="MEOK AI Labs DORA × NIS2 Crosswalk MCP. Maps DORA obligations to NIS2 Article 21-23 measures.",
)

def _server_meter_check(api_key: str = "") -> dict:
    """Calls the live /verify endpoint for server-side metering. Returns the JSON dict.
    Fail-open: if /verify is unreachable or KV isn't configured, returns allowed=True
    (so the local rate-limit in _check_rate_limit remains the safety net)."""
    try:
        data = json.dumps({"api_key": api_key, "tool": ""}).encode()
        req = _meter_urlreq.Request(_METER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with _meter_urlreq.urlopen(req, timeout=2.5) as r:
            d = json.loads(r.read())
            if isinstance(d, dict) and "allowed" in d:
                return d
    except Exception:
        pass
    return {"allowed": True, "tier": "anonymous", "remaining": 200, "upgrade_url": "https://meok.ai/pricing"}


_METER_URL = "https://proofof.ai/verify"


@mcp.tool()
def list_overlapping_obligations(api_key: str = "") -> CrosswalkResponse:
    """Return the full DORA → NIS2 crosswalk table with shared evidence."""
    allowed, msg, tier = _shared_check_access(api_key)
    if not allowed: return {"error": msg}
    if err := _rl(tier): return {"error": err}
    
    crosswalk = {k: ObligationDetail(**v) for k, v in CROSSWALK_DATA.items()}
    return CrosswalkResponse(
        legal_basis="DORA = Regulation (EU) 2022/2554 | NIS2 = Directive (EU) 2022/2555",
        crosswalk=crosswalk,
        overlap_percent_estimate=65,
        disclaimer="Estimate based on practitioner consensus 2024. Not legal advice.",
        upsell_pro=f"Pro £199/mo: {STRIPE_199}" if tier == "free" else None
    )

@mcp.tool()
def compare_reporting_clocks(api_key: str = "") -> ClocksResponse:
    """Show side-by-side DORA vs NIS2 incident-reporting clocks."""
    allowed, msg, tier = _shared_check_access(api_key)
    if not allowed: return {"error": msg}
    
    clocks = {k: ReportingClockDetail(**v) for k, v in REPORTING_CLOCKS_DATA.items()}
    return ClocksResponse(
        reporting_clocks=clocks,
        practical_implication="NIS2 24h early warning is the tightest SLA — design to that clock."
    )

@mcp.tool()
def check_dual_compliance(entity_name: str, controls_csv: str, api_key: str = "") -> ComplianceResponse:
    """Score dual DORA + NIS2 compliance given current controls."""
    allowed, msg, tier = _shared_check_access(api_key)
    if not allowed: return {"error": msg}
    if err := _rl(tier): return {"error": err}

    controls = [c.strip().lower() for c in controls_csv.split(",") if c.strip()]
    results = []
    passes = 0
    for obligation, detail in CROSSWALK_DATA.items():
        satisfies = detail["satisfies_both_if"].lower()
        matches = [c for c in controls if c in satisfies or any(w in satisfies for w in c.split())]
        if len(matches) >= 2:
            state, score = "PASS", 1.0
            passes += 1
        elif matches:
            state, score = "PARTIAL", 0.5
            passes += 0.5
        else:
            state, score = "GAP", 0.0
        results.append(ComplianceObligationResult(
            obligation=obligation,
            nis2_equivalent=detail["nis2_equivalent"],
            state=state,
            satisfies_both_if=detail["satisfies_both_if"],
            matched_controls=matches
        ))

    overall_score = round(100 * passes / len(CROSSWALK_DATA), 1)
    return ComplianceResponse(
        entity=entity_name,
        overall_dual_compliance_percent=overall_score,
        obligations=results,
        upsell_pro=f"Pro £199/mo: {STRIPE_199}" if tier == "free" else None
    )

@mcp.tool()
def sign_dual_compliance_attestation(entity_name: str, overall_score: float, findings_csv: str = "", include_pdf_base64: bool = False, api_key: str = "") -> Dict[str, Any]:
    """Generate a cryptographically signed DORA × NIS2 dual-compliance attestation (Pro+)."""
    allowed, msg, tier = _shared_check_access(api_key)
    if not allowed: return {"error": msg}
    if tier == "free":
        return {"error": "Signed attestations require Pro (£199/mo)", "upgrade_url": STRIPE_199}
    
    findings = [f.strip() for f in findings_csv.split(",") if f.strip()]
    return _attestation(
        regulation="DORA × NIS2 dual compliance",
        entity=entity_name,
        score=overall_score,
        findings=findings or [f"Score: {overall_score}"],
        articles_audited=list(CROSSWALK_DATA.keys()),
        tier=tier,
        include_pdf_base64=include_pdf_base64,
        api_key=api_key,
    )

def main():
    mcp.run()


if __name__ == "__main__":
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/aFa7sNcgAdQS0ZT1Uc8k91t"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
