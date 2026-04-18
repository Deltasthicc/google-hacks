# NyayaLens Monitoring Dashboard (Looker Studio)

## Purpose

This dashboard turns NyayaLens from a one-shot fairness audit tool into a continuous governance surface. It answers four questions that any team running automated decision systems needs to answer on an ongoing basis:

1. What is the fairness posture of our models right now?
2. Which disparity metrics are failing most often, and on which protected attributes?
3. Does our mitigation actually help when we apply it?
4. Which groups are being affected repeatedly across audits, across datasets and models?

All four questions are answered off the same BigQuery table, `fairness.audit_history`, which receives one row per audit run from the FastAPI backend.

## Data source

- **Primary table:** `${project}.fairness.audit_history`
- **Secondary table:** `${project}.fairness.report_exports` (used only for the export-volume card)
- **Partition key:** `created_at` (DAY), so every chart applies a date-range filter to keep scan cost bounded.
- **Refresh cadence:** near-real-time. BigQuery streaming inserts make new audits visible within seconds.

## Layout

The dashboard is one page, divided into four zones top-to-bottom. A left-hand filter panel applies to all zones.

### Zone A: Posture at a glance (three KPI tiles)

- **Audits in window** — COUNT(*) over the filter range.
- **Severe + High audits** — COUNTIF(risk_level IN ('severe','high')), with a delta vs. the prior window.
- **Audits with mitigation applied** — COUNTIF(mitigation_method IS NOT NULL) as a share.

### Zone B: Risk summary over time (stacked area chart)

- **Query:** `dashboard_risk_summary.sql`
- **X axis:** `audit_date`
- **Y axis:** `audit_count`, stacked by `risk_level` in the order severe, high, moderate, low, minimal.
- **Colour mapping:** red for severe, orange for high, amber for moderate, light green for low, dark green for minimal.
- **Why it matters:** shows whether fairness outcomes are getting better or worse over time, which is exactly what a governance stakeholder needs to see first.

### Zone C: Where audits are failing (two charts side by side)

- **Left: Metric failure bars** — from `dashboard_metric_failures.sql`. One bar per protected attribute, stacked by which metric (`demographic_parity`, `equal_opportunity`, `equalized_odds`, `disparate_impact`) crossed its threshold.
- **Right: Top impacted groups** — from `dashboard_group_impact.sql`. Horizontal bar chart of (attribute, group, harm_type) sorted by `times_flagged`. Limited to the top 15 to keep it scannable.

### Zone D: Does mitigation help? (one comparison chart)

- **Query:** `dashboard_mitigation_impact.sql`
- **Visualisation:** grouped bar chart. X axis is mitigation method. For each method, two bars: `avg_dp_before` and `avg_dp_after`. Add a small text caption below each method showing `audits_improved / audits` as a simple ratio.
- **Why it matters:** this chart is the one that turns skeptical reviewers into believers. If the bars shrink after mitigation, the product is doing its job.

### Zone E (optional): Export volume

Single line chart from `report_exports`, showing daily counts broken down by format. Good signal of product adoption for a stretch pitch, but not required for the judging demo.

## Demo script notes

For the live demo, make sure the date filter is set to "last 30 days" and the project filter is set to the hiring or lending demo project. Zones B, C-right, and D are the three that most reward a thirty-second glance. Lead the judge's eye through them in that order: "here is the trend, here is who is being affected, here is whether mitigation is helping."

## Build steps

1. Create the Looker Studio report.
2. Add `audit_history` and `report_exports` as BigQuery custom-query data sources (the four SQL files in `analytics/bigquery/sql/`). Parameterise each with the project and dataset.
3. Build Zone A as three scorecard components.
4. Build Zones B–D as described above.
5. Wire the left-hand filter panel to the shared dimensions: `created_at`, `project_id`, `dataset_name`, `risk_level`, `mitigation_method`.
6. Share the report link in read-only mode. The link goes into `docs/submission/project_links.md`.

## Out of scope for the hackathon

- Row-level drill-through into individual audit records. This is a natural next step but requires a per-audit detail page, which is more UI work than a one-week sprint allows.
- Cross-organisation benchmarking. Requires multi-tenant partitioning and a normalisation strategy we have not yet designed.
- Custom alerting (fire a Slack/email when severe audits exceed a threshold). Documented in the roadmap but not built for submission.
