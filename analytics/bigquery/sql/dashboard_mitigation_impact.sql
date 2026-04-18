-- Mitigation impact: how much fairness improved after each mitigation method.
--
-- Powers the "Does mitigation actually help?" chart. For each audit that
-- has both metrics_before and metrics_after, compute the change in
-- demographic_parity_difference and group by mitigation_method.
--
-- Only rows where mitigation_method is non-null are included.

WITH pre AS (
  SELECT
    audit_id,
    dataset_name,
    model_name,
    mitigation_method,
    created_at,
    JSON_VALUE(attr.value, '$.attribute') AS attribute,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.demographic_parity_difference') AS FLOAT64) AS dp_before,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.equal_opportunity_difference') AS FLOAT64)  AS eo_before
  FROM
    `${project}.${dataset}.audit_history`,
    UNNEST(JSON_QUERY_ARRAY(metrics_before, '$.per_attribute')) AS attr
  WHERE
    mitigation_method IS NOT NULL
    AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
),
post AS (
  SELECT
    audit_id,
    JSON_VALUE(attr.value, '$.attribute') AS attribute,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.demographic_parity_difference') AS FLOAT64) AS dp_after,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.equal_opportunity_difference') AS FLOAT64)  AS eo_after
  FROM
    `${project}.${dataset}.audit_history`,
    UNNEST(JSON_QUERY_ARRAY(metrics_after, '$.per_attribute')) AS attr
  WHERE
    metrics_after IS NOT NULL
    AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
)
SELECT
  pre.mitigation_method,
  COUNT(DISTINCT pre.audit_id)                                      AS audits,
  AVG(ABS(pre.dp_before) - ABS(post.dp_after))                      AS avg_dp_reduction,
  AVG(ABS(pre.eo_before) - ABS(post.eo_after))                      AS avg_eo_reduction,
  AVG(ABS(pre.dp_before))                                           AS avg_dp_before,
  AVG(ABS(post.dp_after))                                           AS avg_dp_after,
  COUNTIF(ABS(post.dp_after) < ABS(pre.dp_before))                  AS audits_improved,
  COUNTIF(ABS(post.dp_after) >= ABS(pre.dp_before))                 AS audits_no_improvement
FROM
  pre
JOIN
  post
  ON pre.audit_id = post.audit_id
  AND pre.attribute = post.attribute
GROUP BY
  pre.mitigation_method
ORDER BY
  avg_dp_reduction DESC;
