-- Load data from CSV files
-- Default location: /tmp/kg-data/
-- If you downloaded the files to a different location, update the paths below

\COPY standards_framework_item FROM '/tmp/kg-data/StandardsFrameworkItem.csv' DELIMITER ',' CSV HEADER;
\COPY standards_framework FROM '/tmp/kg-data/StandardsFramework.csv' DELIMITER ',' CSV HEADER;
\COPY learning_component FROM '/tmp/kg-data/LearningComponent.csv' DELIMITER ',' CSV HEADER;
\COPY relationships FROM '/tmp/kg-data/Relationships.csv' DELIMITER ',' CSV HEADER;