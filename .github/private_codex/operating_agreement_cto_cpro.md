# Operating Agreement — CTO × CPrO

**Owner:** CTO & Chief Prompt Officer
**Last Reviewed:** 2025-10-21

---

## Mission
Ship fast without regressions. The CPrO owns evaluation/safety gates for agentic flows; the CTO owns end-to-end delivery and ship/no-ship decisions.

## Scope
Applies to all changes that affect prompts, agent toolchains, retrieval plans, or inference-time policies used in production write paths or public demos.

## Interfaces (who does what)
- **CPrO**
  - Designs and versions prompt patterns/tool-use plans.
  - Maintains eval harness and golden sets; publishes scorecards.
  - Blocks merges that fail critical evals (see Gates).
- **CTO**
  - Owns architecture, SLIs/SLOs, and incident response.
  - Decides ship/no-ship after gates are satisfied.
  - May request time-bound waivers for non-critical evals (see Waivers).

## Gates (must pass before merge)
1. **Eval Gate (critical flows):**
   - Regression ≤ 0% on golden sets; latency and cost within budget.
   - Safety checks pass (red-team smoke + policy tests).
2. **Tech Gate:** CI green; ADR linked for structural changes.
3. **Comms Gate (if external-facing):** CHRO claim check completed.

## Waivers (exception path)
- **When allowed:** Urgent hotfix or non-critical surface (e.g., copy-only prompt).
- **Process:** CTO opens an ADR addendum noting: scope, risk, rollback, and expiry (≤ 7 days). Founder signs off. CPrO schedules follow-up evals.

## SLAs
- **Eval review:** ≤ 24 business hours.
- **Prompt hotfix in P1 incident:** ≤ 2 hours to mitigated state.
- **Scorecard publish after merge to prod:** ≤ 24 hours.

## Incident Flow (P1 affecting users or public demo)
1. Triage: CTO incident commander; CPrO prompt lead.
2. Mitigate: smallest safe change; document delta.
3. Verify: run targeted eval subset + SLO check.
4. Postmortem: within 48 hours; include eval drift/coverage actions.

## Metrics & Budgets
- **Quality:** Eval coverage % of critical prompts; weekly regression rate.
- **Reliability:** Error-budget burn; p99 latency for inference.
- **Efficiency:** Cost per successful task (eval-defined).

## Dispute Resolution
Data-first comparison of eval deltas + SLO impact. If unresolved, Founder adjudicates within 24 hours.

## Artifacts
- `/evals/` scorecards (CPrO)
- ADR links for structural/prompt-pattern changes (CTO/CPrO)
- Incident postmortems stored under `/ops/incidents/` (CTO)

---
