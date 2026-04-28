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

    # --- Encode target to binary (Generic) ---
    unique_vals = cleaned_df[target_col].unique()
    
    if len(unique_vals) > 2:
        # If it looks like continuous income (many numeric values), binarize at 50k
        print(f"  NOTE: Continuous target detected. Binarizing at 50,000 threshold.")
        income_labels = (cleaned_df[target_col] > 50000).astype(int)
    else:
        # Map the first value to 0, second to 1
        target_map = {unique_vals[0]: 0, unique_vals[1]: 1}
        income_labels = cleaned_df[target_col].map(target_map)

    # --- Extract sensitive columns before dropping ---
    sensitive_data = {}
    for col in sensitive_cols:
        sensitive_data[col] = cleaned_df[col].copy()

    # --- Build features ---
    # Drop target and sensitive columns
    feature_df = cleaned_df.drop(columns=sensitive_cols + [target_col])

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

    # --- Split sensitive columns ---
    if len(sensitive_cols) == 1:
        primary_col = sensitive_cols[0]
        sensitive_train = sensitive_data[primary_col].loc[features_train.index]
        sensitive_test = sensitive_data[primary_col].loc[features_test.index]
    else:
        sensitive_train = cleaned_df[sensitive_cols].loc[features_train.index]
        sensitive_test = cleaned_df[sensitive_cols].loc[features_test.index]

    return {
        "status": "success",
        "features_train": features_train,
        "features_test": features_test,
        "income_labels_train": labels_train,
        "income_labels_test": labels_test,
        "sensitive_train": sensitive_train,
        "sensitive_test": sensitive_test,
    }
