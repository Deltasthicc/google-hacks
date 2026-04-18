-- Weekly audit volume and high-risk counts, last 365 days.
--
-- Powers an optional top-of-dashboard trendline that zooms out to a
-- year-long view. Bucketed by week to keep the chart readable.
--
-- Complements dashboard_risk_summary.sql, which is daily over 90 days.

SELECT
  TIMESTAMP_TRUNC(created_at, WEEK(MONDAY))                    AS week_start,
  COUNT(*)                                                      AS audit_count,
  COUNT(DISTINCT project_id)                                    AS active_projects,
  COUNTIF(risk_level IN ('high', 'severe'))                     AS high_risk_count,
  COUNTIF(mitigation_method IS NOT NULL)                        AS mitigated_count
FROM
  `${project}.${dataset}.audit_history`
WHERE
  created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
GROUP BY
  week_start
ORDER BY
  week_start;
