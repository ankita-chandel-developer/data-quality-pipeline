import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

# Project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from clean_raw_data import CleanRawData
from curated_data import CuratedData
from data_loader import read_csv_files



if __name__ == "__main__":
    logging.info("Starting data processing...")
    logging.info("Reading raw data...")
    raw_data = read_csv_files()
    logging.info("Cleaning raw data...")
    cleaned_data = CleanRawData(raw_data).run()
    logging.info("Curating cleaned data...")
    curated_data = CuratedData(cleaned_data).run()
