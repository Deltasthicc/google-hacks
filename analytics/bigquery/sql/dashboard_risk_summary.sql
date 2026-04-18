-- Risk level distribution over the last 90 days.
--
-- Powers the "Risk posture" card on the monitoring dashboard. Answers
-- the question: of the audits we ran recently, how many came back as
-- minimal/low/moderate/high/severe?
--
-- Partition filter on created_at keeps scan cost proportional to the
-- time window, not the whole table.

SELECT
  DATE(created_at)            AS audit_date,
  risk_level,
  COUNT(*)                    AS audit_count,
  COUNTIF(mitigation_method IS NOT NULL) AS audits_with_mitigation,
  COUNTIF(mitigation_method IS NULL)     AS audits_without_mitigation
FROM
  `${project}.${dataset}.audit_history`
WHERE
  created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY
  audit_date,
  risk_level
ORDER BY
  audit_date DESC,
  CASE risk_level
    WHEN 'severe'   THEN 0
    WHEN 'high'     THEN 1
    WHEN 'moderate' THEN 2
    WHEN 'low'      THEN 3
    WHEN 'minimal'  THEN 4
  END;
