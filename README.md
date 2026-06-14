# Introduction
This project cleans raw data namely actuals, forecasts and objects,transforms it into curated dataset(based on quality checks) and generates the output file along with flags.
The entire solution is implemented using python.

# Features
- Reads raw input CSV files from the 'data/' folder
- Cleans and standardizes data (removes duplicates, fixes formats, checks for missing/invalid values)
- Applies specific quality checks (based on inputs)
- Outputs cleaned and curated datasets with quality flags
- Logs processing steps and issues to log files

# Input files

- Folder: 'data/'
- Files:
   - 'objects.csv'
   - 'actuals.csv'
   - 'forecasts.csv'

# Usage

1. Install dependencies
   All required python libraries are mentioned in the requirements.txt file.

   - pip install -r requirements.txt

2. Run the main script
   -python src/main.py

3. Logs
   Logs will be reported on the screen as the process runs.

4. On successful execution output files will be generated in the output folder.

# Project Structure

src/ 
  main.py  # Entry point- Run this file
  clean_raw_data.py
  curated_data.py
  data_loader.py
  config.py
  utils.py

data/ 
  objects.csv
  actuals.csv
  forecasts.csv

tests/
  test_file.py

output/
  cleaned/
    cleaned_actuals.csv
    cleaned_objects.csv
    cleaned_forecasts.csv
  curated/
     curated_data.csv

# Configuration
Edit `config.py` to update file paths, expected columns or any other variable value as per requirements.

# Output
- Cleaned and curated CSV files in the output directory 

# Assumptions Made

- Input CSV files are present in the `data/` folder and named as specified above.
- Each file contains the expected columns as defined in `config.py`.
- Date and numeric columns may contain invalid or missing values, which will be handled during cleaning.
- Duplicate records are identified based on unique keys (e.g., `object_id`, `timestamp`) and only the first occurrence is kept.
- Only 15-minute interval timestamps are considered valid for actuals and forecasts.
- Status and object type values are validated against allowed lists in `config.py`.
- Output paths and file names can be configured in `config.py`.

# Data Quality issues found
1. Blank client_id rows in objects.csv file. This is raised in 'missing_client_id' flag.
2. Object_id not matching expected format found in actuals.csv. Example: 1001
3. Timestamps were missing in the raw data.
4. Found inactive objects.
5. Duplicate (object_id, timestamp) combinations.
6. Negative energy values found in actuals and forecasts raw data.
7. Missing object metadata.

All the flagged rows are summarized in `data quality issue` column of the curated output as separated strings.

# Improved pipeline in production
1. Orchestration
   - problem: Currently the pipeline runs layers sequentially that is the flow load csv-> clean data-> curated data -> write csv.
   if one step fails there are no retries. 

   - solution: I would solve this by using orchestration tools that will help in independent layers execution, retries and monitoring.

2. Latest data processing
   - problem: Currently the pipeline processes all the data present. 
   - solution: In production I would track the processing via last run using timetsamp and process new or updated records only.

3.  Data validation in the beginning
   - problem: For issues like new column being added or current columns being re-named. Though I have added a config.py for that but it might still not be reliable in production.

   - solution: Adding data ingestion will help in identifying data  related issues in the start of the project rather than failing in between the layers.

4. Storage
   - Problem: Currently the pipeline stores output in CSV file. This could be having huge dataset going forward. This will make 
   data look up difficult.

   - Solution: Having storage systems like sql database can fasten the data lookup process based on simple queries.

# Data model recommendation

I would recommend a three layer data model that will have the following:

1. Raw data layer
   - Storing raw data as it has arrived. This will be used as a referrence in case of failure. This will server for tracking as in what arrived and what has changed.

2. Clean data layer
   - In this layer extra white spaces will be removed, duplicates will be removed, inconsistencies in data will be flagged. Safe to query but not yet joined. This will serve as data preparation before curation process.

3. Curated layer
   - Final analytics table at `timestamp + object_id` grain,
  joined with object metadata, abs_error calculated, quality flags attached.
  This is the layer consumed by reporting and forecasting tools.

This separation makes the pipeline easier to debug as we will know which layer has an issue, reruning layers independently and extend services without touching/overwriting raw or cleaned data.

# Handling late arriving corrections

The problem here is that the value submitted to the grid operator must remain unchanged and the new updated values must be stored at the same time.

I would like to recommend the following solutions-

1. Data model change-
   I would add additional fields such as `version`, `submitted_status`and `replaced_at` to the actuals table.
   The original submitted row is marked with `submitted_status` TRUE, along with correction date in `replaced_at` and never gets modified.  
   Whenever a late correction arrives it is inserted as a new row with incremented version and `replaced_at` as NULL.

2. Preserving version-   
   Having separate views on the table one for the versions where `submitted_status` is TRUE (older submissions) and other for the where `replaced_at` is NULL (latest submissions) will help in no data loss and no data overwriting.

3. Alerting downstream consumers
   
   Whenever a correction arrives for already submitted records the alert system sends notification to the consumers with the old value, corrected value along with the delta. Small correction below a threshold value are ignored to avoid unnecessary alerts. Then the consumers can decide on the action.

   
