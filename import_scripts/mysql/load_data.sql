-- Load data from CSV files
-- Default location: /tmp/kg-data/
-- If you downloaded the files to a different location, update the paths below
-- Note: Use mysql --local-infile=1 when running this script

LOAD DATA LOCAL INFILE '/tmp/kg-data/StandardsFramework.csv'
INTO TABLE standards_framework
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/tmp/kg-data/StandardsFrameworkItem.csv'
INTO TABLE standards_framework_item
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/tmp/kg-data/LearningComponent.csv'
INTO TABLE learning_component
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/tmp/kg-data/Relationships.csv'
INTO TABLE relationships
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;