SELECT
  r."sourceEntityValue",
  r."targetEntityValue",
  r."jaccard",
  r."stateLCCount",
  r."ccssLCCount",
  r."sharedLCCount"
FROM relationships r
JOIN standards_framework_item sfi
  ON sfi."identifier" = r."sourceEntityValue"
WHERE r."relationshipType" = 'hasStandardAlignment'
  AND sfi."statementCode" = '111.26.b.4.D'
  AND sfi."jurisdiction" = 'Texas'
ORDER BY r."jaccard" DESC;
