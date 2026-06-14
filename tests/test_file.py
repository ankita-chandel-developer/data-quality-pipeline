import pytest
import pandas as pd

from src.clean_raw_data import CleanRawData
from src.curated_data import CuratedData

@pytest.fixture
def validate_actuals_df():
    return pd.DataFrame( {
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 00:15:00"],
        "object_id": ["obj_1", "obj_2"],
        "actual_mwh": [100, 150]
    })

@pytest.fixture
def validate_forecasts_df():
    return pd.DataFrame( {
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 00:15:00"],
        "object_id": ["obj_1", "obj_2"],
        "forecast_mwh": [110, 140]
    })

@pytest.fixture
def validate_objects_df():
    return pd.DataFrame( {
        "object_id": ["obj_1", "obj_2"],
        "client_id": ["client_1", "client_2"],
        "object_type": ["solar", "wind"],
        "area": ["area_1", "area_2"],
        "active_from": ["2023-01-01", "2023-01-01"],
        "active_to": ["2025-01-01", "2025-01-01"],
        "installed_capacity_mw": [50, 75],
        "status": ["active", "active"]
    })

def test_validate_actuals(validate_actuals_df):
    assert validate_actuals_df.shape == (2, 3)
    assert set(validate_actuals_df.columns) == {"timestamp", "object_id", "actual_mwh"}


def test_validate_forecasts(validate_forecasts_df):
    assert validate_forecasts_df.shape == (2, 3)
    assert set(validate_forecasts_df.columns) == {"timestamp", "object_id", "forecast_mwh"}


def test_validate_objects(validate_objects_df):
    assert validate_objects_df.shape == (2, 8)
    assert set(validate_objects_df.columns) == {
        "object_id",
        "client_id",
        "object_type",
        "area",
        "active_from",
        "active_to",
        "installed_capacity_mw",
        "status",
    }

def test_curated_data(validate_objects_df, validate_actuals_df, validate_forecasts_df):
    dataset = {
        "objects": validate_objects_df,
        "actuals": validate_actuals_df,
        "forecasts": validate_forecasts_df
    }
    curated_data = CuratedData(dataset).run()
    assert curated_data.shape == (2, 11)  
    assert set(curated_data.columns) == {
        "object_id",
        "client_id",
        "object_type",
        "area",
        "active_from",
        "active_to",
        "installed_capacity_mw",
        "status",
        "timestamp",
        "actual_mwh",
        "forecast_mwh"
    }

def test_cleaned_data(validate_objects_df, validate_actuals_df, validate_forecasts_df):
    dataset = {
        "objects": validate_objects_df,
        "actuals": validate_actuals_df,
        "forecasts": validate_forecasts_df
    }
    cleaned_data = CleanRawData(dataset).run()
    assert cleaned_data["objects"].shape == (2, 16)  
    assert cleaned_data["actuals"].shape == (2, 4)  
    assert cleaned_data["forecasts"].shape == (2, 4)