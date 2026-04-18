-- Most frequently impacted groups across audits.
--
-- Powers the "Who is being affected most often?" chart. Unnests the
-- impacted_groups array from the report_json and counts how often each
-- (attribute, group) pair shows up across audits in the last 90 days.
--
-- This is one of the strongest long-term value queries for the product:
-- it reveals systemic patterns rather than one-off findings.

SELECT
  JSON_VALUE(g.value, '$.attribute')  AS attribute,
  JSON_VALUE(g.value, '$.group')      AS affected_group,
  JSON_VALUE(g.value, '$.harm_type')  AS harm_type,
  COUNT(*)                            AS times_flagged,
  COUNT(DISTINCT audit_id)            AS distinct_audits,
  COUNT(DISTINCT dataset_name)        AS distinct_datasets
FROM
  `${project}.${dataset}.audit_history`,
  UNNEST(JSON_QUERY_ARRAY(report_json, '$.impacted_groups')) AS g
WHERE
  created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY
  attribute,
  affected_group,
  harm_type
ORDER BY
  times_flagged DESC
LIMIT 50;
