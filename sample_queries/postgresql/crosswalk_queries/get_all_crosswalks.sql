SELECT
  "sourceEntityValue",
  "targetEntityValue",
  "jaccard",
  "stateLCCount",
  "ccssLCCount",
  "sharedLCCount"
FROM relationships
WHERE "relationshipType" = 'hasStandardAlignment'
ORDER BY "jaccard" DESC;
