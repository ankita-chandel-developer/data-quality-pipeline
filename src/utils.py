import pandas as pd
import os

def write_csv(df: pd.DataFrame, path: str) -> None:
    """
    Writes a dataframe to a CSV file.
    Args:
        df : The dataframe to write.
        path : The file path to write the CSV to.
    Returns:
        None
    """
    try:
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        df.to_csv(path, index=False)
        print(f"Data successfully written to {path}")
    except Exception as e:
        print(f"Error writing data to CSV: {e}")

def standardizeObjectId(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes the object_id column by stripping whitespace and converting to uppercase.
    Args:
        df (pd.DataFrame): The dataframe containing the object_id column.
    Returns:
        pd.DataFrame: The dataframe with standardized object_id.
    """
    df["object_id"] = df["object_id"].astype(str).str.strip().str.upper()
    return df