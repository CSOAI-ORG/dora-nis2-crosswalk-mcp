# DORA × NIS2 Crosswalk MCP


> ## Buy Starter — £29/mo
> **Signed attestations + unlimited audits + email support.**
> 👉 **[Subscribe at meok.ai](https://buy.stripe.com/aFa5kF1BW146gYRdCU8k83U)** — instant HMAC signing key + Stripe-managed billing.
>
> Free tier remains MIT-licensed and zero-config. Upgrade only when you need signed compliance artefacts for audit.

[![PyPI](https://img.shields.io/pypi/v/dora-nis2-crosswalk-mcp)](https://pypi.org/project/dora-nis2-crosswalk-mcp/) [![Python](https://img.shields.io/pypi/pyversions/dora-nis2-crosswalk-mcp)](https://pypi.org/project/dora-nis2-crosswalk-mcp/)


**Map Regulation (EU) 2022/2554 (DORA) obligations to Directive (EU) 2022/2555 (NIS2) Article 21-23 measures** — so EU banks, insurers, payment institutions, crypto-asset service providers, and their CTPPs can prove dual compliance without re-auditing the same controls twice.

By [MEOK AI Labs](https://meok.ai).

## Why this exists

Most EU financial entities are in scope for **both** DORA and NIS2. The obligations overlap ~65% but:

- Reporting clocks differ (DORA: 4h/72h/1mo — NIS2: 24h/72h/1mo + 3mo progress)
- Competent authorities differ (DORA: national FSA — NIS2: national CSIRT)
- Classification thresholds differ (Commission Delegated Reg (EU) 2024/1772 vs NIS2 national transpositions)

If you treat them as two separate programmes, you duplicate work. If you treat them as one with a crosswalk, you don't.

## Tools

- `list_overlapping_obligations` — full crosswalk table with "satisfies-both-if" test
- `compare_reporting_clocks` — side-by-side incident reporting timeline
- `check_dual_compliance` — score your current controls against both regimes
- `sign_dual_compliance_attestation` — Pro/Enterprise: cryptographically signed dual-compliance cert

## Install

```bash
pip install dora-nis2-crosswalk-mcp
```

## Tiers

- **Free** — 10 queries/day, crosswalk + clocks
- **Pro £199/mo** — unlimited + dual-compliance gap scoring + signed attestations
- **Enterprise £1,499/mo** — multi-entity, gap-remediation export
- **£5,000 assessment** — 48h dual-compliance gap review + roadmap

## Related MEOK MCPs

- [`dora-compliance-mcp`](https://pypi.org/project/dora-compliance-mcp/) — DORA alone
- [`nis2-compliance-mcp`](https://pypi.org/project/nis2-compliance-mcp/) — NIS2 alone
- [`cra-compliance-mcp`](https://pypi.org/project/cra-compliance-mcp/) — EU CRA
- [`meok-attestation-verify`](https://pypi.org/project/meok-attestation-verify/) — verify signed certs

## Full Compliance Platform

Need more than crosswalk mapping? **[councilof.ai](https://councilof.ai)** provides the complete EU regulatory compliance stack — DORA, NIS2, EU AI Act, CRA, CSRD — from £29/mo.

→ **[Get started at councilof.ai](https://councilof.ai)**

> **If this tool helps your compliance workflow, please [star this repo](https://github.com/meok-ai-labs/dora-nis2-crosswalk-mcp/stargazers)** — it helps other teams find it.

## License

MIT — [MEOK AI Labs](https://meok.ai), 2026.

<<<<<<< Updated upstream
=======
<!-- meok-faq-schema-v1 -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is this MCP server free to use?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. The free tier gives you 10 calls per day with no API key required. Pro tier is £79/mo for unlimited calls plus cryptographically signed attestations your auditor can verify independently."
      }
    },
    {
      "@type": "Question",
      "name": "How does the signed attestation work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Every Pro tier audit produces a HMAC-SHA256 signed certificate with a unique ID and a public verify URL. Your auditor pastes the cert into https://meok-attestation-api.vercel.app/verify and gets an independent valid/invalid response. No contact with MEOK required."
      }
    },
    {
      "@type": "Question",
      "name": "Which MCP clients does this work with?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "All standard MCP clients: Claude Desktop, Claude Code, Cursor, VS Code with MCP extension, Windsurf, Cline, and any custom MCP-compatible agent. Install via npx meok-setup or pip install for the underlying Python package."
      }
    },
    {
      "@type": "Question",
      "name": "Can I install all MEOK governance MCPs at once?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. Run npx meok-setup --pack governance to install all 10 governance MCPs and write the configs for Claude Desktop, Cursor, or Windsurf in one command."
      }
    },
    {
      "@type": "Question",
      "name": "Is the regulation text authoritative?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. MEOK syncs daily from the EUR-Lex Cellar SPARQL endpoint, the canonical EU regulation publication system. The text is verbatim with no LLM summarization. Every quote is auditor-defensible and includes the exact article number plus relevance score."
      }
    }
  ]
}
</script>

>>>>>>> Stashed changes

## Sister MCPs

Part of the MEOK **Governance** pack — designed to work together as a fleet. Install the whole pack with `npx meok-setup --pack governance`, or pick the ones you need:

- **EU AI Act** → `uvx eu-ai-act-compliance-mcp` · [PyPI](https://pypi.org/project/eu-ai-act-compliance-mcp/) · [GitHub](https://github.com/CSOAI-ORG/eu-ai-act-compliance-mcp)
- **DORA** → `uvx dora-compliance-mcp` · [PyPI](https://pypi.org/project/dora-compliance-mcp/) · [GitHub](https://github.com/CSOAI-ORG/dora-compliance-mcp)
- **NIS2** → `uvx nis2-compliance-mcp` · [PyPI](https://pypi.org/project/nis2-compliance-mcp/) · [GitHub](https://github.com/CSOAI-ORG/nis2-compliance-mcp)
- **Cyber Resilience Act** → `uvx cra-compliance-mcp` · [PyPI](https://pypi.org/project/cra-compliance-mcp/) · [GitHub](https://github.com/CSOAI-ORG/cra-compliance-mcp)
- **AI Bill of Materials** → `uvx ai-bom-mcp` · [PyPI](https://pypi.org/project/ai-bom-mcp/) · [GitHub](https://github.com/CSOAI-ORG/ai-bom-mcp)
- **AI Incident Reporting** → `uvx ai-incident-reporting-mcp` · [PyPI](https://pypi.org/project/ai-incident-reporting-mcp/) · [GitHub](https://github.com/CSOAI-ORG/ai-incident-reporting-mcp)

Full catalogue + Anthropic Registry verify links: [meok.ai/anthropic-registry](https://meok.ai/anthropic-registry)


## Protocol coverage + Universal PAYG

This MCP is part of MEOK's 47-MCP fleet that bridges every active agent-interop protocol
and 30+ regulatory frameworks. See the full coverage matrix at [meok.ai/protocols](https://meok.ai/protocols).

**Agent interop protocols supported (8 live):**

- ✅ **MCP** (Anthropic) — native
- ✅ **A2A** (Google + Linux Foundation, absorbed IBM ACP Sept 2025)
- ✅ **IBM ACP** — covered via A2A merge
- ◐ **Stripe ACP** (Agentic Commerce Protocol) — Q3 bridge via [agent-commerce-protocol-mcp](https://github.com/CSOAI-ORG/agent-commerce-protocol-mcp)
- ◐ **AP2** (Google Agent Payments) — partial via [agent-commerce-payments-mcp](https://github.com/CSOAI-ORG/agent-commerce-payments-mcp)
- ◐ **x402** (Coinbase HTTP 402) — partial via api.meok.ai gateway
- → **OASF / AGNTCY** (Cisco Outshift + Linux Foundation) — Q3 bridge
- 👁 **ANP** (Cisco Agent Network) — watch-list

**Pricing options:**

| Option | Price | Best for |
|---|---|---|
| Self-host (this MCP) | £0 — MIT | Devs |
| This MCP Starter | £29/mo | One-MCP teams |
| This MCP Pro | £79/mo | Production + 24h SLA |
| [Universal PAYG](https://buy.stripe.com/00w3cxcgAaEGcIBcyQ8k90s) | £29/mo + £0.0002/call | Spiky usage across many MCPs |
| Substrate bundle (this category) | £99-£499/mo | A whole pack |
| [MEOK Universe](https://buy.stripe.com/cNi9AV0xS8wy5g9aqI8k90u) | £1,499/mo | All 47 MCPs, 500K calls |

Each tier above the free self-host adds HMAC-signed attestations verifiable at
`verify.meok.ai`. Linux Foundation governance on the A2A spine means EU regulated
buyers can deploy without vendor-lock-in objections.

<!-- mcp-name: io.github.CSOAI-ORG/dora-nis2-crosswalk-mcp -->
