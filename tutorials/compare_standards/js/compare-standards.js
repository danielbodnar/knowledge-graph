/* ================================
   CONFIGURATION & SETUP
   ================================ */

// Dependencies
const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
require('dotenv').config();

// Domain Constants
// Pick a state standard to find its best CCSSM match
// Note: We need to specify both the code AND jurisdiction since multiple states may use the same code
const TARGET_STATE_STANDARD_CODE = '111.26.b.4.D';  // Texas 6th grade math standard on rates
const TARGET_STATE_JURISDICTION = 'Texas';

// Environment setup
const dataDir = process.env.KG_DATA_PATH;
if (!dataDir) {
  console.error('❌ KG_DATA_PATH environment variable is not set.');
  process.exit(1);
}


/* ================================
   HELPER FUNCTIONS
   ================================ */

function loadCSV(filename) {
  try {
    const content = fs.readFileSync(path.join(dataDir, filename), 'utf8');
    return parse(content, { columns: true, skip_empty_lines: true });
  } catch (error) {
    console.error(`❌ Error loading CSV file ${filename}: ${error.message}`);
    throw error;
  }
}


/* ================================
   STEP 1: LOAD THE CROSSWALK DATA
   ================================ */

function loadCrosswalkData(aq) {
  /**
   * Load crosswalk data from relationships.csv
   *
   * Purpose: Crosswalk data lives in the relationships.csv file. Standards that have
   * crosswalk data include four crosswalk-specific columns: jaccard, stateLCCount,
   * ccssLCCount, and sharedLCCount.
   *
   * Each row shows one state → CCSSM crosswalk relationship.
   */

  // Load CSV files
  const relationshipsData = aq.from(loadCSV('Relationships.csv'));
  const standardsFrameworkItemsData = aq.from(loadCSV('StandardsFrameworkItem.csv'));
  const learningComponentsData = aq.from(loadCSV('LearningComponent.csv'));

  console.log('✅ Data loaded from KG CSV files');
  console.log(`  Total Relationships: ${relationshipsData.numRows()}`);
  console.log(`  Standards Framework Items: ${standardsFrameworkItemsData.numRows()}`);
  console.log(`  Learning Components: ${learningComponentsData.numRows()}`);

  // Filter for crosswalk relationships (hasStandardAlignment)
  const crosswalkData = relationshipsData
    .filter(d => d.relationshipType === 'hasStandardAlignment');

  console.log(`\n✅ Crosswalk data filtered:`);
  console.log(`  Total crosswalk relationships (state → CCSSM): ${crosswalkData.numRows()}`);

  // Show preview of crosswalk data
  if (crosswalkData.numRows() > 0) {
    console.log(`\n📊 Preview of crosswalk data (first 3 rows):`);
    const preview = crosswalkData
      .select('sourceEntityValue', 'targetEntityValue', 'jaccard',
              'stateLCCount', 'ccssLCCount', 'sharedLCCount')
      .slice(0, 3)
      .objects();

    preview.forEach((row, idx) => {
      console.log(`  ${idx + 1}. Source: ${row.sourceEntityValue} → Target: ${row.targetEntityValue}`);
      console.log(`     Jaccard: ${row.jaccard}, State LCs: ${row.stateLCCount}, CCSS LCs: ${row.ccssLCCount}, Shared: ${row.sharedLCCount}`);
    });
  }

  return {
    crosswalkData,
    standardsFrameworkItemsData,
    learningComponentsData,
    relationshipsData
  };
}


/* ================================
   STEP 2: FIND THE BEST-MATCHING CCSSM STANDARD
   ================================ */

function findBestCcssmMatch(stateStandardCode, jurisdiction, data, aq) {
  /**
   * Find the best CCSSM match for a state standard
   *
   * Purpose: To find the best CCSS match for a state standard, filter rows by the
   * state standard ID and sort by the Jaccard score. This identifies the CCSSM
   * standard that contains the most similar skills and concept targets for student
   * mastery (not necessarily the most similar semantically).
   */

  const { crosswalkData, standardsFrameworkItemsData } = data;

  // First, find the state standard by its statement code and jurisdiction
  const stateStandard = standardsFrameworkItemsData
    .params({ code: stateStandardCode, juris: jurisdiction })
    .filter(d => d.statementCode === code && d.jurisdiction === juris)
    .object();

  if (!stateStandard || !stateStandard.statementCode) {
    console.log(`❌ State standard not found: ${stateStandardCode}`);
    return null;
  }

  const stateStandardId = stateStandard.identifier; // Use 'identifier' column for crosswalk matching

  console.log(`✅ Found state standard: ${stateStandardCode}`);
  console.log(`  Identifier: ${stateStandardId}`);
  console.log(`  Description: ${stateStandard.description}`);
  console.log(`  Jurisdiction: ${stateStandard.jurisdiction}`);

  // Filter crosswalk data for this state standard
  const matches = crosswalkData
    .params({ stateId: stateStandardId })
    .filter(d => d.sourceEntityValue === stateId);

  if (matches.numRows() === 0) {
    console.log(`\n❌ No CCSSM matches found for ${stateStandardCode}`);
    return null;
  }

  // Sort by Jaccard score (highest first)
  const sortedMatches = matches.orderby(aq.desc('jaccard'));

  console.log(`\n✅ Found ${sortedMatches.numRows()} CCSSM matches for ${stateStandardCode}`);
  console.log(`\n📊 Top match (highest Jaccard score):`);

  const topMatch = sortedMatches.object();
  console.log(`  CCSSM Standard UUID: ${topMatch.targetEntityValue}`);
  console.log(`  Jaccard Score: ${parseFloat(topMatch.jaccard).toFixed(4)}`);
  console.log(`  Shared LC Count: ${topMatch.sharedLCCount}`);
  console.log(`  State LC Count: ${topMatch.stateLCCount}`);
  console.log(`  CCSS LC Count: ${topMatch.ccssLCCount}`);

  return sortedMatches;
}


/* ================================
   STEP 3: INTERPRET THE RELATIONSHIP METRICS
   ================================ */

function interpretRelationshipMetrics(matches) {
  /**
   * Interpret the relationship metrics for crosswalk matches
   *
   * Purpose: Each crosswalk relationship carries additional context about the degree
   * of overlap:
   * - sharedLCCount shows how many deconstructed skills are shared
   * - stateLCCount and ccssLCCount show how many total skills support each standard
   * - Together with the Jaccard score, these counts help interpret the strength and
   *   balance of the overlap
   */

  if (!matches || matches.numRows() === 0) {
    return;
  }

  console.log(`\n📊 INTERPRETATION OF TOP MATCHES:\n`);

  // Show top 5 matches with interpretation
  const topMatches = matches.slice(0, 5).objects();

  topMatches.forEach((match, idx) => {
    const jaccard = parseFloat(match.jaccard);
    const stateLc = parseFloat(match.stateLCCount);
    const ccssLc = parseFloat(match.ccssLCCount);
    const sharedLc = parseFloat(match.sharedLCCount);

    console.log(`Match #${idx + 1}:`);
    console.log(`  Jaccard Score: ${jaccard.toFixed(4)}`);
    console.log(`  State LC Count: ${stateLc}`);
    console.log(`  CCSS LC Count: ${ccssLc}`);
    console.log(`  Shared LC Count: ${sharedLc}`);

    // Interpret the metrics
    let interpretation;
    if (jaccard >= 0.9) {
      interpretation = "Very strong overlap; standards share nearly all skills";
    } else if (jaccard >= 0.7) {
      interpretation = "Strong overlap; substantial shared skills";
    } else if (jaccard >= 0.5) {
      interpretation = "Moderate overlap; many shared skills";
    } else if (jaccard >= 0.3) {
      interpretation = "Partial overlap; some shared skills";
    } else {
      interpretation = "Weak overlap; few shared skills";
    }

    // Check scope balance
    let scopeNote;
    if (Math.abs(stateLc - ccssLc) <= 2) {
      scopeNote = "Both standards have similar scope";
    } else if (stateLc > ccssLc) {
      scopeNote = "State standard covers more content";
    } else {
      scopeNote = "CCSS standard covers more content";
    }

    console.log(`  Interpretation: ${interpretation}`);
    console.log(`  Scope: ${scopeNote}`);
    console.log();
  });
}


/* ================================
   STEP 4: JOIN CROSSWALKS WITH STANDARDS METADATA
   ================================ */

function enrichCrosswalksWithMetadata(matches, data, aq) {
  /**
   * Join crosswalk data with standards metadata
   *
   * Purpose: Enrich the crosswalk data by joining it with StandardsFrameworkItems.csv,
   * which contains metadata such as grade level and description. This provides a clear
   * view of which state standards most closely align to their CCSSM counterparts, along
   * with the strength of each connection.
   */

  if (!matches || matches.numRows() === 0) {
    return null;
  }

  const { standardsFrameworkItemsData } = data;

  // Rename columns to avoid conflicts when merging state and CCSS metadata
  // We'll merge the same standards dataset twice (once for state, once for CCSS)

  // Join with state standard metadata (source)
  const enriched = matches
    .join(
      standardsFrameworkItemsData.select('identifier', 'statementCode', 'description',
                                         'gradeLevel', 'academicSubject', 'jurisdiction')
        .rename({
          identifier: 'state_identifier',
          statementCode: 'statementCode_state',
          description: 'description_state',
          gradeLevel: 'gradeLevel_state',
          academicSubject: 'academicSubject_state'
        }),
      ['sourceEntityValue', 'state_identifier']
    )
    // Join with CCSS standard metadata (target)
    .join(
      standardsFrameworkItemsData.select('identifier', 'statementCode', 'description',
                                         'gradeLevel', 'academicSubject')
        .rename({
          identifier: 'ccss_identifier',
          statementCode: 'statementCode_ccss',
          description: 'description_ccss',
          gradeLevel: 'gradeLevel_ccss',
          academicSubject: 'academicSubject_ccss'
        }),
      ['targetEntityValue', 'ccss_identifier']
    );

  console.log(`\n✅ Enriched crosswalk data with standards metadata\n`);
  console.log(`📊 DETAILED COMPARISON (Top 3 matches):\n`);

  const top3 = enriched.slice(0, 3).objects();

  top3.forEach((row, idx) => {
    console.log(`Match #${idx + 1} (Jaccard: ${parseFloat(row.jaccard).toFixed(4)}):`);
    console.log(`  STATE STANDARD:`);
    console.log(`    Code: ${row.statementCode_state}`);
    console.log(`    Jurisdiction: ${row.jurisdiction}`);
    console.log(`    Grade Level: ${row.gradeLevel_state}`);
    console.log(`    Description: ${row.description_state}`);
    console.log(`  `);
    console.log(`  CCSS STANDARD:`);
    console.log(`    Code: ${row.statementCode_ccss}`);
    console.log(`    Grade Level: ${row.gradeLevel_ccss}`);
    console.log(`    Description: ${row.description_ccss}`);
    console.log(`  `);
    console.log(`  ALIGNMENT METRICS:`);
    console.log(`    Shared LCs: ${row.sharedLCCount} / State LCs: ${row.stateLCCount} / CCSS LCs: ${row.ccssLCCount}`);
    console.log();
  });

  return enriched;
}


/* ================================
   STEP 5: JOIN CROSSWALKS TO LEARNING COMPONENTS
   ================================ */

function showSharedLearningComponents(stateStandardCode, ccssStandardCode, stateJurisdiction, data, aq) {
  /**
   * Join crosswalks to Learning Components to show shared skills
   *
   * Purpose: Now that you have crosswalk pairs (state → CCSSM), you can see the
   * actual skills behind each match by joining to the Learning Components dataset.
   * We'll use the 'supports' relationships to fetch the LCs that support each standard
   * and then intersect them to list the shared LCs (the evidence behind the crosswalk).
   */

  const { standardsFrameworkItemsData, relationshipsData, learningComponentsData } = data;

  // Find the standard identifiers
  // Note: For LC relationships, we need to use caseIdentifierUUID, not identifier
  const stateStandard = standardsFrameworkItemsData
    .params({ code: stateStandardCode, juris: stateJurisdiction })
    .filter(d => d.statementCode === code && d.jurisdiction === juris)
    .object();

  const ccssStandard = standardsFrameworkItemsData
    .params({ code: ccssStandardCode })
    .filter(d => d.statementCode === code && d.jurisdiction === 'Multi-State')
    .object();

  if (!stateStandard || !ccssStandard) {
    console.log('❌ Could not find one or both standards');
    return;
  }

  const stateUuid = stateStandard.caseIdentifierUUID;
  const ccssUuid = ccssStandard.caseIdentifierUUID;

  // Get LCs that support the state standard
  // LC relationships use caseIdentifierUUID for targetEntityValue
  const stateLcIds = relationshipsData
    .params({ uuid: stateUuid })
    .filter(d => d.relationshipType === 'supports' && d.targetEntityValue === uuid)
    .array('sourceEntityValue');

  const stateLcs = learningComponentsData
    .filter(aq.escape(d => stateLcIds.includes(d.identifier)))
    .select('identifier', 'description')
    .dedupe('identifier');

  // Get LCs that support the CCSS standard
  const ccssLcIds = relationshipsData
    .params({ uuid: ccssUuid })
    .filter(d => d.relationshipType === 'supports' && d.targetEntityValue === uuid)
    .array('sourceEntityValue');

  const ccssLcs = learningComponentsData
    .filter(aq.escape(d => ccssLcIds.includes(d.identifier)))
    .select('identifier', 'description')
    .dedupe('identifier');

  // Find shared LCs (intersection) using join
  const sharedLcs = stateLcs
    .semijoin(ccssLcs, 'identifier');

  // Find state-only LCs (in state but not in CCSS)
  const stateOnlyLcs = stateLcs
    .antijoin(ccssLcs, 'identifier');

  // Find CCSS-only LCs (in CCSS but not in state)
  const ccssOnlyLcs = ccssLcs
    .antijoin(stateLcs, 'identifier');

  console.log(`\n✅ LEARNING COMPONENTS ANALYSIS:\n`);
  console.log(`State Standard: ${stateStandardCode}`);
  console.log(`CCSS Standard: ${ccssStandardCode}`);
  console.log();

  console.log(`📊 SHARED LEARNING COMPONENTS (${sharedLcs.numRows()}):`);
  console.log('These are the concrete pedagogical overlaps between the two standards:\n');
  sharedLcs.objects().forEach((lc, idx) => {
    console.log(`  ✅ ${idx + 1}. ${lc.description}`);
  });
  console.log();

  console.log(`📊 STATE-ONLY LEARNING COMPONENTS (${stateOnlyLcs.numRows()}):`);
  stateOnlyLcs.objects().forEach((lc, idx) => {
    console.log(`  ➖ ${idx + 1}. ${lc.description}`);
  });
  console.log();

  console.log(`📊 CCSS-ONLY LEARNING COMPONENTS (${ccssOnlyLcs.numRows()}):`);
  ccssOnlyLcs.objects().forEach((lc, idx) => {
    console.log(`  ➕ ${idx + 1}. ${lc.description}`);
  });
  console.log();
}


/* ================================
   MAIN EXECUTION
   ================================ */

async function main() {
  const aq = await import('arquero');

  console.log('\n=== USING CROSSWALKS TO COMPARE STATE STANDARDS TO COMMON CORE ===\n');

  console.log('🔄 Step 1: Load the crosswalk data...');
  const data = loadCrosswalkData(aq);

  console.log('\n' + '='.repeat(70));
  console.log('🔄 Step 2: Find the best-matching CCSSM standard for a state standard...');
  const matches = findBestCcssmMatch(TARGET_STATE_STANDARD_CODE, TARGET_STATE_JURISDICTION, data, aq);

  if (matches && matches.numRows() > 0) {
    console.log('\n' + '='.repeat(70));
    console.log('🔄 Step 3: Interpret the relationship metrics...');
    interpretRelationshipMetrics(matches);

    console.log('='.repeat(70));
    console.log('🔄 Step 4: Join crosswalks with standards metadata...');
    const enriched = enrichCrosswalksWithMetadata(matches, data, aq);

    if (enriched && enriched.numRows() > 0) {
      console.log('='.repeat(70));
      console.log('🔄 Step 5: Join crosswalks to Learning Components...');
      // Use the top match for detailed LC analysis
      const topMatch = enriched.object();
      showSharedLearningComponents(
        topMatch.statementCode_state,
        topMatch.statementCode_ccss,
        topMatch.jurisdiction,
        data,
        aq
      );
    }
  }
}

main().catch(console.error);
