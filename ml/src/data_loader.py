"""
Data loader for FairLens AI / NyayaLens.

Loads the UCI Adult (Census Income) dataset from OpenML,
returning a clean pandas DataFrame ready for preprocessing.
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
