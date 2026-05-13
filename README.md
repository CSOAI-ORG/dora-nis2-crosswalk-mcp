# DORA × NIS2 Crosswalk MCP

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

<!-- mcp-name: io.github.CSOAI-ORG/dora-nis2-crosswalk-mcp -->
