-- Get all Texas crosswalks with state standard information
-- Returns Texas state → CCSSM standard alignments ordered by Jaccard score

SELECT
  state."statementCode" AS state_standard_code,
  state."jurisdiction" AS state_jurisdiction,
  r."sourceEntityValue",
  r."targetEntityValue",
  r."jaccard",
  r."stateLCCount",
  r."ccssLCCount",
  r."sharedLCCount"
FROM relationships r
JOIN standards_framework_item state
  ON state."caseIdentifierUUID" = r."sourceEntityValue"
WHERE r."relationshipType" = 'hasStandardAlignment'
  AND state."jurisdiction" = 'Texas'
ORDER BY r."jaccard" DESC;
