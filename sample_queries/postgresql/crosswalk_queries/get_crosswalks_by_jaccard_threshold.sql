-- Get all crosswalks that meet or exceed a specified Jaccard similarity threshold
-- Ordered by state jurisdiction, CCSSM standard code, then Jaccard score

SELECT
  state_std."jurisdiction" AS state_jurisdiction,
  state_std."statementCode" AS state_standard_code,
  ccss_std."statementCode" AS ccss_standard_code,
  r."jaccard",
  r."sharedLCCount",
  r."stateLCCount",
  r."ccssLCCount"
FROM relationships r
JOIN standards_framework_item state_std
  ON state_std."caseIdentifierUUID" = r."sourceEntityValue"
JOIN standards_framework_item ccss_std
  ON ccss_std."caseIdentifierUUID" = r."targetEntityValue"
WHERE r."relationshipType" = 'hasStandardAlignment'
  AND r."jaccard" >= 0.7
ORDER BY
  state_std."jurisdiction",
  ccss_std."statementCode",
  r."jaccard" DESC;
