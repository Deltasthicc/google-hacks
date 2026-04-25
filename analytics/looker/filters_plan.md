# Filters Plan

The left-hand filter panel in the Looker dashboard. Every filter below applies to all charts on the page, with the exceptions noted.

## Filters

| Filter | Type | Source field | Default | Notes |
|---|---|---|---|---|
| Date range | Date range | `created_at` | Last 30 days | All queries are partitioned on `created_at`, so this filter directly reduces scan cost. |
| Project | Single-select dropdown | `project_id` | All projects | Use for demo mode: pick the lending or hiring demo project to reset all charts to that context. |
| Dataset | Multi-select dropdown | `dataset_name` | All datasets | Allows scoping to a specific benchmark (e.g. "show only ACSIncome runs"). |
| Protected attribute | Multi-select dropdown | unnested `protected_attributes` | All attributes | Applied via a custom `UNNEST` in the Looker data source. Does not apply to Zone A KPIs. |
| Risk level | Multi-select dropdown | `risk_level` | All levels | Does not apply to Zone B (which visualises the risk distribution by definition). |
| Mitigation method | Multi-select dropdown | `mitigation_method` | All methods (including null) | Allows a reviewer to ask "what did threshold_optimizer do vs reweighing?" |
| Task type | Single-select dropdown | `task_type` | All | Useful once we have both tabular and NLP runs in the table. |

## Filter interactions to avoid

- **Do not** apply the "Risk level" filter to Zone B. The whole point of the risk trend chart is to show the distribution across all levels.
- **Do not** apply the "Mitigation method" filter to Zone D's left bar (`avg_dp_before`), since that reflects pre-mitigation state and should be method-agnostic.

## Filter defaults for the demo

When sharing the dashboard link for the judges, pre-set:

- **Date range:** Last 30 days
- **Project:** Demo Lending Project (or Demo Hiring Project)
- All other filters: All

This ensures the dashboard looks populated and coherent on first load, rather than the default "Last 7 days with no data" state.

## Stretch: saved views

Looker supports per-report saved views. Three views would be useful if time allows:

- **Executive view.** Only Zone A and Zone B visible. One-screen summary for an exec sponsor.
- **ML Engineer view.** Zone C and Zone D emphasised. For the person who has to act on findings.
- **Compliance view.** All zones, with date range widened to 90 days. For auditing the audits.
