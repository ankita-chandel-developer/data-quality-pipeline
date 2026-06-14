import pandas as pd
import logging
from config import *
from src.utils import write_csv

class CuratedData:
    def __init__(self, data: dict[str, pd.DataFrame]):
        self.dataset = data
    
    def data_issues(self, row) -> list[str]:
        issues = [
            flag
            for flag in QUALITY_FLAGS
            if row.get(flag, False)
        ]

        return issues

    def data_quality_checks(self, curated_df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs data quality checks on the curated dataframe.
        Args:
            df (pd.DataFrame): The dataframe to check.
        Returns:
            pd.DataFrame: The dataframe with quality check results.
        """
        logging.info("Performing data quality checks...")
    
        df=curated_df.copy()
        try:
            #1. Calculate abs error
            df["abs_error"] = (df["actual_mwh"] - df["forecast_mwh"]).abs()

            #2. Missing Objects in metadata
            df["missing_metadata"] = df["client_id"].isna()

            #3. Missing/Invalid timestamps in actuals or forecasts
            df["missing_timestamp"] = df["timestamp"].isna()
            
            #4. forecasts or actuals for inactive objects
            df["inactive_object"] = (
                (df["timestamp"] < df["active_from"]) 
                | 
                (df["active_to"].notna() & (df["timestamp"] > df["active_to"]))
            )

            #5. Negative Energy Values
            df["negative_energy_value"] = (
                (df["actual_mwh"] < 0)
                |
                (df["forecast_mwh"] < 0)
            )

            #6. Suspicious installed capacity
            df["suspicious_installed_capacity"] = df["installed_capacity_mw"].isna() | (df["installed_capacity_mw"] > MAX_REASONABLE_CAPACITY) | (df["installed_capacity_mw"] < 0)

            #7. Invalid object Id pattern
            df["invalid_object_id"] = ~df["object_id"].isna() & ~df["object_id"].astype(str).str.match(EXPECTED_OBJECT_ID_PATTERN)

            #8. Duplicate timestamp and object_id combinations
            df["duplicate_timestamp_object_id"] = df.duplicated(subset=["timestamp", "object_id"])


            #9. Is valid record check
            df["is_valid_record"] = ~df[QUALITY_FLAGS].any(axis=1)

            #10. Data quality check
            df["data_quality_issue"] = df.apply(self.data_issues, axis=1).apply(lambda x: ", ".join(x) if x else None)
        
        except Exception as e:
            logging.error(f"Error during data quality checks: {e}")

        return df

    def merge_curated_data(self)->pd.DataFrame:
        """
        Runs the data curation process.
        Args:
            None
        Returns:
            pd.DataFrame: The curated dataframe.
        """
        logging.info("Running curated data generation process...")
        curated_output = pd.DataFrame()
        try:
            actuals_df = self.dataset.get("actuals", pd.DataFrame())
            forecasts_df = self.dataset.get("forecasts", pd.DataFrame())        
            objects_df = self.dataset.get("objects", pd.DataFrame())
            
            #Filter revelant columns
            actuals_df = actuals_df[ACTUALS_COLS]
            forecasts_df = forecasts_df[FORECASTS_COLS]
            objects_df = objects_df[OBJECT_COLS]

            # Merge actuals and forecasts on timestamp and object_id
            curated_df= actuals_df.merge(
                forecasts_df,
                on=["timestamp","object_id"],
                how="outer"
            )
            
            # Merge the above result with objects on object_id
            curated_output= curated_df.merge(
                objects_df,
                on="object_id",
                how="left"
            )
            logging.info(f"Curated dataset: {len(curated_output)} rows")

            
        except Exception as e:
            logging.error(f"Error during merging curated data: {e}")
            raise e
        
        return curated_output

        

    def run(self) -> pd.DataFrame:
        """
        Runs the data curation process and performs quality checks.
        Args:
            None
        Returns:
            pd.DataFrame: The curated dataframe.
        """
        logging.info("Merging cleaned data to create curated dataset...")
        curated_data = self.merge_curated_data()

        logging.info("Performing data quality checks on curated dataset...")
        curated_output_data = self.data_quality_checks(curated_data)
        curated_output_data= curated_output_data[CURATED_COLUMNS]

        #Write curated data to csv
        logging.info("Writing curated data to CSV file...")
        write_csv(curated_output_data, FILE_PATHS["curated"]["path"])
        return curated_output_data
