SELECT
  state_std."statementCode" AS state_standard_code,
  state_std."jurisdiction" AS state_jurisdiction,
  ccss_std."statementCode" AS ccss_standard_code,
  r."jaccard",
  r."stateLCCount",
  r."ccssLCCount",
  r."sharedLCCount"
FROM relationships r
JOIN standards_framework_item state_std
  ON state_std."identifier" = r."sourceEntityValue"
JOIN standards_framework_item ccss_std
  ON ccss_std."identifier" = r."targetEntityValue"
WHERE r."relationshipType" = 'hasStandardAlignment'
  AND r."jaccard" >= 0.7
ORDER BY r."jaccard" DESC;
