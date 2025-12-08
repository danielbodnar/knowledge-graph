-- Find the best Texas state standard matches for a given CCSSM standard
-- Returns crosswalks ordered by Jaccard score (highest similarity first)
-- with metadata about both the CCSSM and matching Texas state standards

SELECT
  -- CCSSM Standard Information
  ccss."statementCode" AS ccss_standard_code,
  ccss."description" AS ccss_description,
  ccss."gradeLevel" AS ccss_grade_level,
  ccss."jurisdiction" AS ccss_jurisdiction,

  -- State Standard Information
  state."statementCode" AS state_standard_code,
  state."description" AS state_description,
  state."gradeLevel" AS state_grade_level,
  state."jurisdiction" AS state_jurisdiction,

  -- Crosswalk Metrics
  r."jaccard",
  r."sharedLCCount",
  r."stateLCCount",
  r."ccssLCCount",

  -- Entity Values for further joins if needed
  r."sourceEntityValue" AS state_uuid,
  r."targetEntityValue" AS ccss_uuid
FROM relationships r
JOIN standards_framework_item state
  ON state."caseIdentifierUUID" = r."sourceEntityValue"
JOIN standards_framework_item ccss
  ON ccss."caseIdentifierUUID" = r."targetEntityValue"
WHERE r."relationshipType" = 'hasStandardAlignment'
  AND ccss."statementCode" = '6.EE.B.5'
  AND ccss."jurisdiction" = 'Multi-State'
  AND state."jurisdiction" = 'Texas'
ORDER BY r."jaccard" DESC
LIMIT 10;
