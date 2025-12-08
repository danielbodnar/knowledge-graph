-- Get all crosswalks for a specific state jurisdiction
-- Returns comprehensive metadata for both state and CCSSM standards
-- Ordered by state standard code and Jaccard score

SELECT
  -- State Standard Information
  state_std."jurisdiction" AS state_jurisdiction,
  state_std."statementCode" AS state_standard_code,
  state_std."gradeLevel" AS state_grade_level,
  state_std."description" AS state_description,
  state_std."academicSubject" AS state_academic_subject,

  -- CCSSM Standard Information
  ccss_std."statementCode" AS ccss_standard_code,
  ccss_std."gradeLevel" AS ccss_grade_level,
  ccss_std."description" AS ccss_description,
  ccss_std."academicSubject" AS ccss_academic_subject,

  -- Crosswalk Metrics
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
  AND state_std."jurisdiction" = 'Texas'
  AND state_std."academicSubject" = 'Mathematics'
ORDER BY
  state_std."statementCode",
  ccss_std."statementCode",
  r."jaccard" DESC;
