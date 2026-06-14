RAW_FILES = {
    "objects": {
        "file": "objects.csv",
        "expected_columns":[
                "object_id",
                "client_id",
                "object_type",
                "area",
                "active_from",
                "active_to",
                "installed_capacity_mw",
                "status"
        ]
    },
    "actuals": {
        "file": "actuals.csv",
        "expected_columns": [
            "timestamp",
            "object_id",
            "actual_mwh"
        ]
    },
    "forecasts": {
        "file": "forecasts.csv",
        "expected_columns": [
            "timestamp",
            "object_id",
            "forecast_mwh"
        ]
    }
}

FILE_PATHS =  {
    "objects": {
        "path": "output/cleaned/cleaned_objects.csv"
    },
    "actuals": {
        "path": "output/cleaned/cleaned_actuals.csv"
    },
    "forecasts": {
        "path": "output/cleaned/cleaned_forecasts.csv"
    },

    "curated": {
        "path": "output/curated/curated_data_.csv"
    }
}

OBJECT_TYPES = ["solar", "wind", "hydro", "bess", "consumer"]
STATUS_TYPES = ["active", "inactive"]

# Forecast and Actual columns for validation and processing
ACTUALS_COLS = [
    "timestamp",
    "object_id",
    "actual_mwh"
]

FORECASTS_COLS = [
    "timestamp",
    "object_id",
    "forecast_mwh"
]

OBJECT_COLS = [
    "object_id",
    "client_id",
    "object_type",
    "area",
    "active_from",
    "active_to",
    "installed_capacity_mw",
    "status"
]

# Curated Data Quality Check Configurations
EXPECTED_OBJECT_ID_PATTERN = r"^OBJ_\d+$"

MAX_REASONABLE_CAPACITY = 5000


QUALITY_FLAGS = [
    "missing_metadata",
    "missing_timestamp",
    "inactive_object",
    "negative_energy_value",
    "suspicious_installed_capacity",
    "invalid_object_id",
    "duplicate_timestamp_object_id"
]

CURATED_COLUMNS = [
    "timestamp",
    "object_id",
    "client_id",
    "object_type",
    "area",
    "actual_mwh",
    "forecast_mwh",
    "abs_error",
    "is_valid_record",
    "data_quality_issue"
]