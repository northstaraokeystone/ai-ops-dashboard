# StatusCard.tsx Component Transfer

**API:** Props: { title: string, kpiKey: keyof KPIStore } — fetches value/color/trend/badge from Zustand.

**States:** Stateless; reactive to kpiStore (Zustand) for real-time updates (e.g., SSE-driven KPIs).

**a11y:** ARIA-labelledby for card/title; sr-only for trend descriptions; contrast-checked (Tailwind); axe-tested.

**Deps:** react, zustand, shadcn/ui (card/badge), lucide-react (icons).

**Why:** Foundational for Overview Trinity; enables aha clarity (<10-min truth run) with verifiable KPIs; efficient (<50ms render, virtualized); ties to SUN-1/3 moats via reactive, auditable state.
