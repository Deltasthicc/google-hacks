-- Which disparity metrics fail most often, grouped by protected attribute.
--
-- Powers the "Where are audits failing?" chart. Unnests the per_attribute
-- disparities from metrics_before and counts how often each one exceeds
-- a fairness threshold.
--
-- Thresholds are expressed as configurable CTE so judges and organizations
-- can see and tune them. Defaults match the Vertex AI and Fairlearn
-- conventions for tabular classification.

WITH thresholds AS (
  SELECT
    0.10 AS demographic_parity_difference_threshold,
    0.10 AS equal_opportunity_difference_threshold,
    0.10 AS equalized_odds_difference_threshold,
    0.80 AS disparate_impact_ratio_min
),
per_attribute AS (
  SELECT
    DATE(created_at)                                 AS audit_date,
    audit_id,
    dataset_name,
    JSON_VALUE(attr.value, '$.attribute')            AS attribute,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.demographic_parity_difference') AS FLOAT64) AS dp_diff,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.equal_opportunity_difference') AS FLOAT64)  AS eo_diff,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.equalized_odds_difference') AS FLOAT64)     AS eqo_diff,
    SAFE_CAST(JSON_VALUE(attr.value, '$.disparities.disparate_impact_ratio') AS FLOAT64)        AS di_ratio
  FROM
    `${project}.${dataset}.audit_history`,
    UNNEST(JSON_QUERY_ARRAY(metrics_before, '$.per_attribute')) AS attr WITH OFFSET AS idx
  WHERE
    created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
)
SELECT
  pa.attribute,
  COUNT(DISTINCT pa.audit_id) AS total_audits,
  COUNTIF(ABS(pa.dp_diff)   > t.demographic_parity_difference_threshold) AS fails_demographic_parity,
  COUNTIF(ABS(pa.eo_diff)   > t.equal_opportunity_difference_threshold)  AS fails_equal_opportunity,
  COUNTIF(ABS(pa.eqo_diff)  > t.equalized_odds_difference_threshold)     AS fails_equalized_odds,
  COUNTIF(pa.di_ratio       < t.disparate_impact_ratio_min)              AS fails_disparate_impact
FROM
  per_attribute pa,
  thresholds t
GROUP BY
  pa.attribute
ORDER BY
  fails_demographic_parity DESC,
  fails_equal_opportunity  DESC;
