# Chart Plan

One line per chart. Shape, underlying query, purpose, and the judge-facing takeaway it must deliver at a glance.

| Chart ID | Zone | Type | Query | Purpose | Takeaway at a glance |
|---|---|---|---|---|---|
| `kpi_audits_in_window` | A | Scorecard | `SELECT COUNT(*) FROM audit_history WHERE created_at BETWEEN @start AND @end` | Total volume of audits in the selected window. | "We are actually using this product." |
| `kpi_severe_high_audits` | A | Scorecard with delta | Derived from `dashboard_risk_summary.sql` | Count of audits marked severe or high. Delta compares to the prior window of equal length. | "How much of our volume is flagged as concerning right now?" |
| `kpi_mitigation_share` | A | Scorecard | `COUNTIF(mitigation_method IS NOT NULL) / COUNT(*)` on `audit_history` | Percent of audits where mitigation was actually applied. | "Are we following through on fairness findings, or just logging them?" |
| `chart_risk_trend` | B | Stacked area chart | `dashboard_risk_summary.sql` | Risk level distribution per day, last 90 days. | "Is the fairness posture getting better or worse?" |
| `chart_metric_failures` | C-left | Stacked bar chart | `dashboard_metric_failures.sql` | Per protected attribute, how often each disparity metric crosses its threshold. | "Which attributes are the repeat offenders, and which metric is flagging them?" |
| `chart_group_impact` | C-right | Horizontal bar chart | `dashboard_group_impact.sql` | Top (attribute, group, harm_type) combinations by frequency. | "Who is being affected most often across our audits?" |
| `chart_mitigation_impact` | D | Grouped bar chart | `dashboard_mitigation_impact.sql` | For each mitigation method, avg disparity before vs. after. | "Does reweighing/threshold tuning actually close the gap?" |
| `chart_export_volume` | E | Line chart | `report_exports` aggregated by day and format | Daily export counts. | "Is the product being used beyond the initial scan?" (stretch) |

## Chart-level design rules

- **Colour.** Use red / orange / amber / light green / dark green for risk levels. Never use red for "mitigation succeeded" or green for "disparity stayed high." The intuitive mapping matters more than brand palette here.
- **Labels.** Human-readable over canonical. In Zone C-left, rename `demographic_parity_difference` to "Approval rate gap" in the axis labels, and keep the canonical name only in the tooltip.
- **Numbers.** Round every displayed value to two decimal places. Raw metric output will be noisy otherwise.
- **Empty state.** Every chart must render something sensible when the filter returns zero rows. A "no audits match these filters" message is acceptable. Silent empty charts are not.

## Chart-to-query binding sanity checks

Before publishing, confirm each chart renders correctly against at least one sample row. Use the two sample payloads (`lending_sample.json`, `hiring_sample.json`) inserted into a scratch BigQuery project for this. If `chart_metric_failures` shows zeros, the JSON paths in the query are wrong.
