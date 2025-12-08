#!/usr/bin/env python3
"""
Using crosswalks to compare state standards to Common Core

This tutorial demonstrates how to use the crosswalk data in Knowledge Graph to compare
standards between a state framework and the Common Core State Standards (CCSSM). These
crosswalks help determine which CCSSM standard is most similar to a given state standard
and understand the similarities and differences between them.

Crosswalks are evidence-based relationships between state standards and CCSSM standards,
derived from overlapping sets of Learning Components (LCs). Each crosswalk includes
similarity metrics, such as the Jaccard score and relative LC counts, to help interpret
how closely two standards align.
"""

"""
================================
CONFIGURATION & SETUP
================================
"""

# Dependencies
import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Domain Constants
# Pick a CCSSM standard to find its best state standard matches
TARGET_CCSSM_STANDARD_CODE = '6.EE.B.5'  # Common Core 6th grade math standard on solving equations and inequalities
TARGET_CCSSM_JURISDICTION = 'Multi-State'

# Environment Setup
data_dir = os.getenv('KG_DATA_PATH')
if not data_dir:
    print('❌ KG_DATA_PATH environment variable is not set.')
    sys.exit(1)

data_path = Path(data_dir)


"""
================================
HELPER FUNCTIONS
================================
"""

def load_csv(filename):
    """
    Load and parse CSV file from data directory

    Args:
        filename (str): Name of the CSV file to load

    Returns:
        pd.DataFrame: Loaded CSV data as DataFrame
    """
    try:
        file_path = data_path / filename
        return pd.read_csv(file_path, low_memory=False)
    except Exception as error:
        print(f'❌ Error loading CSV file {filename}: {str(error)}')
        raise error


"""
================================
STEP 1: LOAD THE CROSSWALK DATA
================================
"""

def load_crosswalk_data():
    """
    Load crosswalk data from relationships.csv

    Purpose: Crosswalk data lives in the relationships.csv file. Standards that have
    crosswalk data include four crosswalk-specific columns: jaccard, stateLCCount,
    ccssLCCount, and sharedLCCount.

    Each row shows one state → CCSSM crosswalk relationship.

    Returns:
        dict: Dictionary containing crosswalk data and related datasets
    """
    # Load CSV files
    relationships_data = load_csv('Relationships.csv')
    standards_framework_items_data = load_csv('StandardsFrameworkItem.csv')
    learning_components_data = load_csv('LearningComponent.csv')

    print('✅ Data loaded from KG CSV files')
    print(f'  Total Relationships: {len(relationships_data)}')
    print(f'  Standards Framework Items: {len(standards_framework_items_data)}')
    print(f'  Learning Components: {len(learning_components_data)}')

    # Filter for crosswalk relationships (hasStandardAlignment)
    crosswalk_data = relationships_data[
        relationships_data['relationshipType'] == 'hasStandardAlignment'
    ].copy()

    print(f'\n✅ Crosswalk data filtered:')
    print(f'  Total crosswalk relationships (state → CCSSM): {len(crosswalk_data)}')

    # Show preview of crosswalk data
    if len(crosswalk_data) > 0:
        print(f'\n📊 Preview of crosswalk data (first 3 rows):')
        preview_cols = ['sourceEntityValue', 'targetEntityValue', 'jaccard',
                       'stateLCCount', 'ccssLCCount', 'sharedLCCount']
        available_cols = [col for col in preview_cols if col in crosswalk_data.columns]
        print(crosswalk_data[available_cols].head(3).to_string(index=False))

    return {
        'crosswalk_data': crosswalk_data,
        'standards_framework_items_data': standards_framework_items_data,
        'learning_components_data': learning_components_data,
        'relationships_data': relationships_data
    }


"""
================================
STEP 2: FIND THE BEST-MATCHING STATE STANDARDS
================================
"""

def find_best_state_matches(ccssm_standard_code, jurisdiction, data):
    """
    Find the best state standard matches for a CCSSM standard

    Purpose: To find the best state standard matches for a CCSSM standard, filter rows by the
    CCSSM standard ID and sort by the Jaccard score. This identifies the state
    standards that contain the most similar skills and concept targets for student
    mastery (not necessarily the most similar semantically).

    Args:
        ccssm_standard_code (str): The statement code of the CCSSM standard
        jurisdiction (str): The jurisdiction of the CCSSM standard (typically 'Multi-State')
        data (dict): Dictionary containing the loaded datasets

    Returns:
        pd.DataFrame: Crosswalk matches sorted by Jaccard score (highest first)
    """
    crosswalk_data = data['crosswalk_data']
    standards_data = data['standards_framework_items_data']

    # First, find the CCSSM standard by its statement code and jurisdiction
    ccssm_standard = standards_data[
        (standards_data['statementCode'] == ccssm_standard_code) &
        (standards_data['jurisdiction'] == jurisdiction)
    ]

    if len(ccssm_standard) == 0:
        print(f'❌ CCSSM standard not found: {ccssm_standard_code}')
        return None

    ccssm_standard = ccssm_standard.iloc[0]
    ccssm_standard_uuid = ccssm_standard['caseIdentifierUUID']  # Use 'caseIdentifierUUID' for crosswalk matching

    print(f'✅ Found CCSSM standard: {ccssm_standard_code}')
    print(f'  Case UUID: {ccssm_standard_uuid}')
    print(f'  Description: {ccssm_standard["description"]}')
    print(f'  Jurisdiction: {ccssm_standard["jurisdiction"]}')

    # Filter crosswalk data for this CCSSM standard (it's the target in relationships)
    # and filter for Texas matches only
    matches = crosswalk_data[
        crosswalk_data['targetEntityValue'] == ccssm_standard_uuid
    ].copy()

    if len(matches) == 0:
        print(f'\n❌ No state standard matches found for {ccssm_standard_code}')
        return None

    # Join with standards data to get jurisdiction and filter for Texas
    matches = matches.merge(
        standards_data[['caseIdentifierUUID', 'jurisdiction']],
        left_on='sourceEntityValue',
        right_on='caseIdentifierUUID',
        how='left',
        suffixes=('', '_temp')
    )

    # Filter for Texas only
    texas_matches = matches[matches['jurisdiction'] == 'Texas'].copy()

    if len(texas_matches) == 0:
        print(f'\n❌ No Texas standard matches found for {ccssm_standard_code}')
        return None

    # Drop the temporary columns added for filtering
    texas_matches = texas_matches.drop(columns=['caseIdentifierUUID', 'jurisdiction'])

    # Sort by Jaccard score (highest first)
    texas_matches = texas_matches.sort_values('jaccard', ascending=False)

    print(f'\n✅ Found {len(texas_matches)} Texas standard matches for {ccssm_standard_code}')
    print(f'\n📊 Top Texas match (highest Jaccard score):')

    top_match = texas_matches.iloc[0]
    print(f'  State Standard UUID: {top_match["sourceEntityValue"]}')
    print(f'  Jaccard Score: {top_match["jaccard"]:.4f}')
    print(f'  Shared LC Count: {top_match["sharedLCCount"]}')
    print(f'  State LC Count: {top_match["stateLCCount"]}')
    print(f'  CCSS LC Count: {top_match["ccssLCCount"]}')

    return texas_matches


"""
================================
STEP 3: INTERPRET THE RELATIONSHIP METRICS
================================
"""

def interpret_relationship_metrics(matches):
    """
    Interpret the relationship metrics for crosswalk matches

    Purpose: Each crosswalk relationship carries additional context about the degree
    of overlap:
    - sharedLCCount shows how many deconstructed skills are shared
    - stateLCCount and ccssLCCount show how many total skills support each standard
    - Together with the Jaccard score, these counts help interpret the strength and
      balance of the overlap

    Args:
        matches (pd.DataFrame): Crosswalk matches from Step 2
    """
    if matches is None or len(matches) == 0:
        return

    print(f'\n📊 INTERPRETATION OF TOP MATCHES:\n')

    # Show top 5 matches with interpretation
    for idx, (_, match) in enumerate(matches.head(5).iterrows(), 1):
        jaccard = match['jaccard']
        state_lc = match['stateLCCount']
        ccss_lc = match['ccssLCCount']
        shared_lc = match['sharedLCCount']

        print(f'Match #{idx}:')
        print(f'  Jaccard Score: {jaccard:.4f}')
        print(f'  State LC Count: {state_lc}')
        print(f'  CCSS LC Count: {ccss_lc}')
        print(f'  Shared LC Count: {shared_lc}')

        # Interpret the metrics
        if jaccard >= 0.9:
            interpretation = "Very strong overlap; standards share nearly all skills"
        elif jaccard >= 0.7:
            interpretation = "Strong overlap; substantial shared skills"
        elif jaccard >= 0.5:
            interpretation = "Moderate overlap; many shared skills"
        elif jaccard >= 0.3:
            interpretation = "Partial overlap; some shared skills"
        else:
            interpretation = "Weak overlap; few shared skills"

        # Check scope balance
        if abs(state_lc - ccss_lc) <= 2:
            scope_note = "Both standards have similar scope"
        elif state_lc > ccss_lc:
            scope_note = "State standard covers more content"
        else:
            scope_note = "CCSS standard covers more content"

        print(f'  Interpretation: {interpretation}')
        print(f'  Scope: {scope_note}')
        print()


"""
================================
STEP 4: JOIN CROSSWALKS WITH STANDARDS METADATA
================================
"""

def enrich_crosswalks_with_metadata(matches, data):
    """
    Join crosswalk data with standards metadata

    Purpose: Enrich the crosswalk data by joining it with StandardsFrameworkItems.csv,
    which contains metadata such as grade level and description. This provides a clear
    view of which state standards most closely align to their CCSSM counterparts, along
    with the strength of each connection.

    Args:
        matches (pd.DataFrame): Crosswalk matches from Step 2
        data (dict): Dictionary containing the loaded datasets

    Returns:
        pd.DataFrame: Enriched crosswalk data with metadata
    """
    if matches is None or len(matches) == 0:
        return None

    standards_data = data['standards_framework_items_data']

    # Rename columns to avoid conflicts when merging CCSS and state metadata
    # We'll merge the same standards dataset twice (once for CCSS, once for state)

    # Join with CCSS standard metadata (target)
    ccss_standards = standards_data[['caseIdentifierUUID', 'statementCode', 'description',
                                     'gradeLevel', 'academicSubject', 'jurisdiction']].copy()
    ccss_standards.columns = ['ccss_uuid', 'statementCode_ccss', 'description_ccss',
                              'gradeLevel_ccss', 'academicSubject_ccss', 'jurisdiction_ccss']

    enriched = matches.merge(
        ccss_standards,
        left_on='targetEntityValue',
        right_on='ccss_uuid',
        how='left'
    )

    # Join with state standard metadata (source)
    state_standards = standards_data[['caseIdentifierUUID', 'statementCode', 'description',
                                      'gradeLevel', 'academicSubject', 'jurisdiction']].copy()
    state_standards.columns = ['state_uuid', 'statementCode_state', 'description_state',
                               'gradeLevel_state', 'academicSubject_state', 'jurisdiction']

    enriched = enriched.merge(
        state_standards,
        left_on='sourceEntityValue',
        right_on='state_uuid',
        how='left'
    )

    print(f'\n✅ Enriched crosswalk data with standards metadata\n')
    print(f'📊 DETAILED COMPARISON (Top 3 matches):\n')

    for idx, (_, row) in enumerate(enriched.head(3).iterrows(), 1):
        print(f'Match #{idx} (Jaccard: {row["jaccard"]:.4f}):')
        print(f'  CCSS STANDARD:')
        print(f'    Code: {row["statementCode_ccss"]}')
        print(f'    Jurisdiction: {row["jurisdiction_ccss"]}')
        print(f'    Grade Level: {row["gradeLevel_ccss"]}')
        print(f'    Description: {row["description_ccss"]}')
        print(f'  ')
        print(f'  STATE STANDARD:')
        print(f'    Code: {row["statementCode_state"]}')
        print(f'    Jurisdiction: {row["jurisdiction"]}')
        print(f'    Grade Level: {row["gradeLevel_state"]}')
        print(f'    Description: {row["description_state"]}')
        print(f'  ')
        print(f'  ALIGNMENT METRICS:')
        print(f'    Shared LCs: {row["sharedLCCount"]} / State LCs: {row["stateLCCount"]} / CCSS LCs: {row["ccssLCCount"]}')
        print()

    return enriched


"""
================================
STEP 5: JOIN CROSSWALKS TO LEARNING COMPONENTS
================================
"""

def show_shared_learning_components(state_standard_code, ccss_standard_code, state_jurisdiction, data):
    """
    Join crosswalks to Learning Components to show shared skills

    Purpose: Now that you have crosswalk pairs (state → CCSSM), you can see the
    actual skills behind each match by joining to the Learning Components dataset.
    We'll use the 'supports' relationships to fetch the LCs that support each standard
    and then intersect them to list the shared LCs (the evidence behind the crosswalk).

    Args:
        state_standard_code (str): State standard code
        ccss_standard_code (str): CCSS standard code
        state_jurisdiction (str): State jurisdiction (to ensure correct standard match)
        data (dict): Dictionary containing the loaded datasets
    """
    standards_data = data['standards_framework_items_data']
    relationships_data = data['relationships_data']
    learning_components_data = data['learning_components_data']

    # Find the standard identifiers
    # Note: For LC relationships, we need to use caseIdentifierUUID, not identifier
    state_standard = standards_data[
        (standards_data['statementCode'] == state_standard_code) &
        (standards_data['jurisdiction'] == state_jurisdiction)
    ]
    ccss_standard = standards_data[
        (standards_data['statementCode'] == ccss_standard_code) &
        (standards_data['jurisdiction'] == 'Multi-State')
    ]

    if len(state_standard) == 0 or len(ccss_standard) == 0:
        print('❌ Could not find one or both standards')
        return

    state_uuid = state_standard.iloc[0]['caseIdentifierUUID']
    ccss_uuid = ccss_standard.iloc[0]['caseIdentifierUUID']

    # Get LCs that support the state standard
    # LC relationships use caseIdentifierUUID for targetEntityValue
    state_lc_relationships = relationships_data[
        (relationships_data['relationshipType'] == 'supports') &
        (relationships_data['targetEntityValue'] == state_uuid)
    ]

    state_lc_ids = state_lc_relationships['sourceEntityValue'].unique()
    state_lcs = learning_components_data[
        learning_components_data['identifier'].isin(state_lc_ids)
    ][['identifier', 'description']].drop_duplicates()

    # Get LCs that support the CCSS standard
    ccss_lc_relationships = relationships_data[
        (relationships_data['relationshipType'] == 'supports') &
        (relationships_data['targetEntityValue'] == ccss_uuid)
    ]

    ccss_lc_ids = ccss_lc_relationships['sourceEntityValue'].unique()
    ccss_lcs = learning_components_data[
        learning_components_data['identifier'].isin(ccss_lc_ids)
    ][['identifier', 'description']].drop_duplicates()

    # Find shared LCs (intersection) using merge
    shared_lcs = state_lcs.merge(
        ccss_lcs[['identifier']],
        on='identifier',
        how='inner'
    )

    # Find state-only LCs (in state but not in CCSS)
    state_only_lcs = state_lcs[
        ~state_lcs['identifier'].isin(ccss_lcs['identifier'])
    ]

    # Find CCSS-only LCs (in CCSS but not in state)
    ccss_only_lcs = ccss_lcs[
        ~ccss_lcs['identifier'].isin(state_lcs['identifier'])
    ]

    print(f'\n✅ LEARNING COMPONENTS ANALYSIS:\n')
    print(f'CCSS Standard: {ccss_standard_code}')
    print(f'State Standard: {state_standard_code}')
    print()

    print(f'📊 SHARED LEARNING COMPONENTS ({len(shared_lcs)}):')
    print('These are the concrete pedagogical overlaps between the two standards:\n')
    for idx, (_, lc) in enumerate(shared_lcs.iterrows(), 1):
        print(f'  ✅ {idx}. {lc["description"]}')
    print()

    print(f'📊 STATE-ONLY LEARNING COMPONENTS ({len(state_only_lcs)}):')
    for idx, (_, lc) in enumerate(state_only_lcs.iterrows(), 1):
        print(f'  ➖ {idx}. {lc["description"]}')
    print()

    print(f'📊 CCSS-ONLY LEARNING COMPONENTS ({len(ccss_only_lcs)}):')
    for idx, (_, lc) in enumerate(ccss_only_lcs.iterrows(), 1):
        print(f'  ➕ {idx}. {lc["description"]}')
    print()


"""
================================
MAIN EXECUTION
================================
"""

def main():
    """
    Main execution function - orchestrates all tutorial steps
    """
    print('\n=== USING CROSSWALKS TO COMPARE STATE STANDARDS TO COMMON CORE ===\n')

    print('🔄 Step 1: Load the crosswalk data...')
    data = load_crosswalk_data()

    print('\n' + '='*70)
    print('🔄 Step 2: Find the best-matching state standards for a CCSSM standard...')
    matches = find_best_state_matches(TARGET_CCSSM_STANDARD_CODE, TARGET_CCSSM_JURISDICTION, data)

    if matches is not None and len(matches) > 0:
        print('\n' + '='*70)
        print('🔄 Step 3: Interpret the relationship metrics...')
        interpret_relationship_metrics(matches)

        print('='*70)
        print('🔄 Step 4: Join crosswalks with standards metadata...')
        enriched = enrich_crosswalks_with_metadata(matches, data)

        if enriched is not None and len(enriched) > 0:
            print('='*70)
            print('🔄 Step 5: Join crosswalks to Learning Components...')
            # Use the top match for detailed LC analysis (already filtered for Texas)
            top_match = enriched.iloc[0]
            show_shared_learning_components(
                top_match['statementCode_state'],
                top_match['statementCode_ccss'],
                top_match['jurisdiction'],
                data
            )


if __name__ == '__main__':
    main()
