"""
Preprocessing module for FairLens AI / NyayaLens.

Cleans raw data, encodes features, separates sensitive columns,
scales features, and splits into train/test sets.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def preprocess(df, target_col="income", sensitive_cols=None):
    """
    Clean, encode, and split a DataFrame for bias-aware model training.

    Steps performed:
        1. Drop rows with '?' or NaN values
        2. Encode target column to binary (1 = positive class, 0 = negative)
        3. Separate sensitive columns (do NOT feed them into the model)
        4. Drop sensitive columns + 'fnlwgt' from feature matrix
        5. One-hot encode remaining categorical columns
        6. Train/test split (80/20)
        7. StandardScaler on all features

    Args:
        df:              pandas DataFrame — raw data (e.g., from CSV upload).
        target_col:      Name of the target column. For the Adult dataset
                         loaded via OpenML, this is 'class'. For uploaded CSVs
                         it might be 'income'. Defaults to 'income'.
        sensitive_cols:  List of column names that are sensitive attributes
                         (e.g., ['sex']). Defaults to ['sex'] if None.

    Returns:
        A dict with status='success' and keys:
            features_train, features_test,
            income_labels_train, income_labels_test,
            sensitive_train, sensitive_test,
            feature_names
        OR a dict with status='error' and a message if something is wrong.
    """
    if sensitive_cols is None:
        sensitive_cols = ["sex"]

    # --- Input validation ---
    if target_col not in df.columns:
        return {
            "status": "error",
            "message": f"Column '{target_col}' not found. Available: {list(df.columns)}",
        }

    for col in sensitive_cols:
        if col not in df.columns:
            return {
                "status": "error",
                "message": f"Sensitive column '{col}' not found. Available: {list(df.columns)}",
            }

    cleaned_df = df.copy()

    # --- Drop rows with '?' or NaN ---
    for column_name in cleaned_df.columns:
        if cleaned_df[column_name].dtype == object:
            has_question_mark = cleaned_df[column_name] == "?"
            cleaned_df = cleaned_df[~has_question_mark]
    cleaned_df = cleaned_df.dropna()

    # --- Encode target to binary ---
    income_labels = cleaned_df[target_col].apply(
        lambda value: 1 if ">50K" in str(value) else 0
    )

    # --- Extract sensitive columns before dropping ---
    sensitive_data = {}
    for col in sensitive_cols:
        sensitive_data[col] = cleaned_df[col].copy()

    # --- Drop sensitive columns, fnlwgt, race, and target from features ---
    columns_to_drop = sensitive_cols + [target_col]
    for extra_col in ["fnlwgt", "race"]:
        if extra_col in cleaned_df.columns and extra_col not in columns_to_drop:
            columns_to_drop.append(extra_col)

    feature_df = cleaned_df.drop(columns=columns_to_drop)

    # --- One-hot encode categoricals ---
    feature_df = pd.get_dummies(feature_df, drop_first=True)

    # --- Train/test split ---
    features_train, features_test, labels_train, labels_test = train_test_split(
        feature_df, income_labels, test_size=0.2, random_state=42
    )

    # --- Scale features ---
    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(features_train)
    scaled_test = scaler.transform(features_test)

    features_train = pd.DataFrame(
        scaled_train, columns=features_train.columns, index=features_train.index
    )
    features_test = pd.DataFrame(
        scaled_test, columns=features_test.columns, index=features_test.index
    )

    # --- Split sensitive columns to match train/test ---
    sensitive_train_dict = {}
    sensitive_test_dict = {}
    for col in sensitive_cols:
        sensitive_train_dict[col] = sensitive_data[col].loc[features_train.index]
        sensitive_test_dict[col] = sensitive_data[col].loc[features_test.index]

    # For single sensitive column, also provide flat Series for convenience
    if len(sensitive_cols) == 1:
        primary_col = sensitive_cols[0]
        sensitive_train = sensitive_train_dict[primary_col]
        sensitive_test = sensitive_test_dict[primary_col]
    else:
        sensitive_train = pd.DataFrame(sensitive_train_dict)
        sensitive_test = pd.DataFrame(sensitive_test_dict)

    return {
        "status": "success",
        "features_train": features_train,
        "features_test": features_test,
        "income_labels_train": labels_train,
        "income_labels_test": labels_test,
        "sensitive_train": sensitive_train,
        "sensitive_test": sensitive_test,
        "feature_names": list(features_train.columns),
    }
