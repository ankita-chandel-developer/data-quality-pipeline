import pandas as pd
import sys
import logging
from pathlib import Path
from config import RAW_FILES

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def read_csv_files()->dict[str, pd.DataFrame]:
    """
    Reads the CSV files and loads them into dataframes.
    Args:
        None
    Returns:
        dict[str, pd.DataFrame]: A dictionary mapping file names to their dataframes.
    """

    # Dictionary to hold the raw data
    raw_data = {}

    try:
        for file_name, path in RAW_FILES.items():
            file_path = PROJECT_ROOT / 'data' / path.get("file")
            logging.info(f"Reading file: {file_path}")  
            if not file_path.exists():
                logging.error(f"File not found: {file_path}")
                sys.exit(1)
            raw_data[file_name] = pd.read_csv(file_path)
    except Exception as e:
        logging.error(f"Error reading CSV files: {e}")
        sys.exit(1)

    return raw_data 