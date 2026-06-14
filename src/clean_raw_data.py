import pandas as pd
import logging
from pathlib import Path
from config import *
from utils import write_csv, standardizeObjectId



class CleanRawData:
    def __init__(self, data: dict[str, pd.DataFrame]):
        self.dataset = data

    def check_expected_columns(self) -> bool:
        """
        Checks if the dataframe contains the expected columns.
        Args:
            dataset (dict[str, pd.DataFrame]): A dictionary mapping file names to their dataframes.

        Returns:
            bool: True if all expected columns are present, False otherwise.
        """
        missing_columns_report = {}
        try:
            for key, config in RAW_FILES.items():
                missing_columns = [col for col in config.get("expected_columns", []) if col not in self.dataset.get(key, pd.DataFrame()).columns]
                if missing_columns:
                    missing_columns_report[key] = missing_columns
                    logging.info(f"Missing columns in {key}: {missing_columns}")
            
            if missing_columns_report:
                logging.error(f"Missing columns report: {missing_columns_report}")
                return False
        except Exception as e:
            logging.error(f"Error checking expected columns: {e}")
            return False

        return True

    def clean_objects(self, objects_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the objects dataframe.
        Args:
            objects_df (pd.DataFrame): The objects dataframe to clean.

        Returns:
            pd.DataFrame: The cleaned objects dataframe.
        """
        objects_clean = objects_df.copy()
        objects_clean = standardizeObjectId(objects_clean)

        # Removing extra spaces
        objects_clean["client_id"] = objects_clean["client_id"].str.strip()
        objects_clean["object_type"] = objects_clean["object_type"].astype(str).str.strip()
        objects_clean["area"] = objects_clean["area"].astype(str).str.strip()

        # Fixing date formats
        objects_clean["active_from"] = pd.to_datetime(objects_clean["active_from"], errors='coerce')
        objects_clean["active_to"] = pd.to_datetime(objects_clean["active_to"], errors='coerce')
        objects_clean["installed_capacity_mw"] = pd.to_numeric(objects_clean["installed_capacity_mw"], errors='coerce')

        # Adding Missing checks 
        objects_clean["missing_object_id"] = objects_clean["object_id"].isna()
        objects_clean["missing_client_id"] = objects_clean["client_id"].isin(["", "nan", "none", "null"])
        
        # quality checks on metadata
        objects_clean["invalid_capacity"] =  (objects_clean["installed_capacity_mw"].isna() | objects_clean["installed_capacity_mw"] <= 0)
        objects_clean["invalid_active_period"] = (
            objects_clean["active_to"].notna()
            & objects_clean["active_from"].notna()
            & (objects_clean["active_to"] < objects_clean["active_from"])
        )
        objects_clean["invalid_status"] = ~objects_clean["status"].isin(STATUS_TYPES)
        objects_clean["invalid_object_type"] = ~objects_clean["object_type"].isin(OBJECT_TYPES)

        objects_clean["duplicate_object_id"] = objects_clean.duplicated(subset=["object_id"], keep=False)
        count_duplicates = objects_clean["duplicate_object_id"].sum()
        if count_duplicates:
            logging.info(f"[objects] Dropping {count_duplicates} duplicate object_id rows")

        #Removing duplicates
        objects_clean = objects_clean.drop_duplicates(subset=["object_id"], keep="first")
        
        return objects_clean

    def clean_actual_forecasts(self, df: pd.DataFrame, value_column: str) -> pd.DataFrame:
        """
        Cleans the actuals and forecasts dataframes.
        Args:
            df (pd.DataFrame): The dataframe to clean.
            value_column (str): The name of the column containing the values (actual_mwh or forecast_mwh).
        Returns:
            pd.DataFrame: The cleaned dataframe.
        """

        cleaned_df = df.copy()

        cleaned_df = standardizeObjectId(cleaned_df)

        # Timestamp
        cleaned_df["timestamp"] = pd.to_datetime(cleaned_df["timestamp"], errors="coerce")

        # Numeric
        cleaned_df[value_column] = pd.to_numeric(cleaned_df[value_column], errors="coerce")
    
        # QUALITY FLAGS
        cleaned_df["invalid_timestamp"] = cleaned_df["timestamp"].isna()

        cleaned_df["invalid_time_interval"] = (
            cleaned_df["timestamp"].notna() &
            ~cleaned_df["timestamp"].dt.minute.isin([0, 15, 30, 45])
        )

        cleaned_df["invalid_value"] = cleaned_df[value_column].isna()

        cleaned_df["negative_value"] = cleaned_df[value_column] < 0

        cleaned_df["missing_object_id"] = cleaned_df["object_id"].isna() | (cleaned_df["object_id"].fillna("").str.strip() == "")

        cleaned_df["duplicate_record"] = cleaned_df.duplicated(
            subset=["object_id", "timestamp"],
            keep=False
        )

        duplicate_count = cleaned_df["duplicate_record"].sum()
        if duplicate_count: 
            logging.info(f"[{value_column}] Dropping {duplicate_count} duplicate object_id and timestamp rows")

        # Remove duplicates
        cleaned_df = cleaned_df.drop_duplicates(subset=["object_id", "timestamp"], keep="first")

        return cleaned_df



    def run(self) -> dict[str, pd.DataFrame]:
        """Runs the cleaning process and returns the cleaned dataframe."""
        if not self.check_expected_columns():
            raise ValueError("Dataframe does not contain all expected columns.")
        
        #________________Cleaning Steps________________
        #-----------------------------------------------
        # CLEAN OBJECTS
        #------------------------------------------------
        logging.info("Cleaning objects dataframe...")
        self.dataset["objects"] = self.clean_objects(self.dataset["objects"])

        #------------------------------------------------
        # CLEAN ACTUALS
        #------------------------------------------------
        logging.info("Cleaning actuals dataframe...")
        self.dataset["actuals"] = self.clean_actual_forecasts(self.dataset["actuals"],"actual_mwh")

        #------------------------------------------------
        # CLEAN FORECASTS
        #------------------------------------------------
        logging.info("Cleaning forecasts dataframe...")
        self.dataset["forecasts"] = self.clean_actual_forecasts(self.dataset["forecasts"],"forecast_mwh")

        # Write cleaned data to csv
        logging.info("Writing cleaned data to CSV files...")
        write_csv(self.dataset["objects"], FILE_PATHS["objects"]["path"])
        write_csv(self.dataset["actuals"], FILE_PATHS["actuals"]["path"])
        write_csv(self.dataset["forecasts"], FILE_PATHS["forecasts"]["path"])

        return self.dataset