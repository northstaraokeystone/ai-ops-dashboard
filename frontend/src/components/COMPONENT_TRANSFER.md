# StatusCard.tsx Component Transfer

**API:** Props: { title: string, kpiKey: keyof KPIStore } — fetches value/color/trend/badge from Zustand.

**States:** Stateless; reactive to kpiStore (Zustand) for real-time updates (e.g., SSE-driven KPIs).

**a11y:** ARIA-labelledby for card/title; sr-only for trend descriptions; contrast-checked (Tailwind); axe-tested.

**Deps:** react, zustand, shadcn/ui (card/badge), lucide-react (icons).

**Why:** Foundational for Overview Trinity; enables aha clarity (<10-min truth run) with verifiable KPIs; efficient (<50ms render, virtualized); ties to SUN-1/3 moats via reactive, auditable state.

# AccountabilityTable.tsx Component Transfer

**API:** Props: None (stateless container); Outputs: Sortable/expandable table of incidents.

**States:** Relies on incidentStore (Zustand) for data/expand/sort; reactive to updates (e.g., SSE).

**a11y:** ARIA-label for table/expands/buttons; sortable headers with indicators; axe-tested.

**Deps:** react, react-table (TanStack), lucide-react (icons), zustand, tailwind (styles).

**Why:** Centerpiece for Triage Level 2; enables interactive "drill-down to truth" with verifiable payloads; efficient (<500ms render/1000 rows, virtualized); ties to SUN-1/3 via triage/assignment tools.

# IncidentWorkbench.tsx Component Transfer

**API:** Props: { incidentId: string, trigger: ReactNode } — fetches/render modal on trigger.

**States:** Local useState for open; relies on incidentStore for data.

**a11y:** ARIA-describedby for content; dialog role; axe-tested.

**Deps:** react, shadcn/ui (dialog), ./ActionButton, zustand, tailwind (styles).

**Why:** Final "action" layer for Level 3; closes 10-min truth run loop with verifiable recovery; efficient (<200ms open, parallel actions); ties to SUN-1/3 via drill-down engine.
