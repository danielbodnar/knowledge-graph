SELECT
  state_std."statementCode" AS state_standard_code,
  state_std."jurisdiction" AS state_jurisdiction,
  state_std."gradeLevel" AS state_grade_level,
  state_std."description" AS state_description,
  ccss_std."statementCode" AS ccss_standard_code,
  ccss_std."gradeLevel" AS ccss_grade_level,
  ccss_std."description" AS ccss_description,
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
  AND state_std."statementCode" = '111.26.b.4.D'
  AND state_std."jurisdiction" = 'Texas'
ORDER BY r."jaccard" DESC;
