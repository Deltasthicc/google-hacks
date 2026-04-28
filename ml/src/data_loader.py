"""
Data loader for FairLens AI / NyayaLens.

Provides utilities for loading standard benchmark datasets (like Adult)
and custom user-uploaded CSV files.
"""

import pandas as pd
from sklearn.datasets import fetch_openml


def load_adult_dataset():
    """
    Download the UCI Adult dataset from OpenML and return it as a DataFrame.

    The Adult dataset contains ~48K rows of US Census data. The prediction
    task is whether a person earns >50K/year. Common sensitive attributes
    are 'sex' and 'race'.

    Args:
        None

    Returns:
        raw_dataframe: pandas DataFrame with all 15 columns including the
                       target column named 'class'.
    """
    adult_bunch = fetch_openml("adult", version=2, as_frame=True)
    raw_dataframe = adult_bunch.frame
    return raw_dataframe


def load_openml_dataset(name_or_id, version=1):
    """
    Generic helper to load any dataset from OpenML by name or ID.
    """
    if isinstance(name_or_id, int):
        bunch = fetch_openml(data_id=name_or_id, as_frame=True, parser="auto")
    else:
        bunch = fetch_openml(name=name_or_id, version=version, as_frame=True, parser="auto")
    return bunch.frame


def load_csv_dataset(csv_path):
    """
    Load a dataset from a local CSV file path.

    This is the entry point Person 2's backend will use when a user
    uploads their own CSV.

    Args:
        csv_path: String path to the CSV file on disk.

    Returns:
        dataframe: pandas DataFrame with the CSV contents.
        If the file is not found, returns a dict with status='error'.
    """
    try:
        dataframe = pd.read_csv(csv_path)
        return dataframe
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"File not found: {csv_path}",
        }
