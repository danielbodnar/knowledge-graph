WITH state_lcs AS (
  SELECT lc.`identifier`, lc.`description`
  FROM relationships r
  JOIN standards_framework_item sfi
    ON sfi.`caseIdentifierUUID` = r.`targetEntityValue`
  JOIN learning_component lc
    ON lc.`identifier` = r.`sourceEntityValue`
  WHERE r.`relationshipType` = 'supports'
    AND sfi.`statementCode` = '111.26.b.4.D'
    AND sfi.`jurisdiction` = 'Texas'
),
ccss_lcs AS (
  SELECT lc.`identifier`, lc.`description`
  FROM relationships r
  JOIN standards_framework_item sfi
    ON sfi.`caseIdentifierUUID` = r.`targetEntityValue`
  JOIN learning_component lc
    ON lc.`identifier` = r.`sourceEntityValue`
  WHERE r.`relationshipType` = 'supports'
    AND sfi.`statementCode` = '6.RP.A.2'
    AND sfi.`jurisdiction` = 'Multi-State'
)
SELECT
  'shared' AS lc_type,
  state_lcs.`identifier`,
  state_lcs.`description`
FROM state_lcs
INNER JOIN ccss_lcs
  ON state_lcs.`identifier` = ccss_lcs.`identifier`

UNION ALL

SELECT
  'state_only' AS lc_type,
  state_lcs.`identifier`,
  state_lcs.`description`
FROM state_lcs
LEFT JOIN ccss_lcs
  ON state_lcs.`identifier` = ccss_lcs.`identifier`
WHERE ccss_lcs.`identifier` IS NULL

UNION ALL

SELECT
  'ccss_only' AS lc_type,
  ccss_lcs.`identifier`,
  ccss_lcs.`description`
FROM ccss_lcs
LEFT JOIN state_lcs
  ON ccss_lcs.`identifier` = state_lcs.`identifier`
WHERE state_lcs.`identifier` IS NULL;
