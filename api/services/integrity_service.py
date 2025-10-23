import numpy as np
import pandas as pd


def validate_data_integrity(records: list[dict], target_col: str | None = None) -> dict:
    df = pd.DataFrame(records)
    missing_by_col = df.isnull().mean().to_dict()
    missing_score = 1.0 - np.mean(list(missing_by_col.values()))
    schema_issues = 0
    if "SeniorCitizen" in df.columns and df["SeniorCitizen"].dtype in [
        "int64",
        "float64",
    ]:
        schema_issues += 1
    schema_score = 1.0 - (schema_issues / len(df.columns))
    duplicate_score = 1.0 - (df.duplicated().sum() / len(df)) if len(df) > 0 else 1.0

    imbalance_score = None
    if target_col and target_col in df.columns:
        counts = df[target_col].value_counts(normalize=True)
        if len(counts) >= 2:
            imbalance_score = 1.0 - (abs(counts.iloc[0] - 0.5) * 2)

    weights = {"completeness": 0.3, "schema": 0.2, "duplicates": 0.2, "imbalance": 0.3}
    if imbalance_score is not None:
        score = (
            missing_score * weights["completeness"]
            + schema_score * weights["schema"]
            + duplicate_score * weights["duplicates"]
            + imbalance_score * weights["imbalance"]
        ) * 100
    else:
        total_weight = (
            weights["completeness"] + weights["schema"] + weights["duplicates"]
        )
        score = (
            (
                missing_score * weights["completeness"]
                + schema_score * weights["schema"]
                + duplicate_score * weights["duplicates"]
            )
            / total_weight
        ) * 100

    alert_level = "RISK" if score < 80 else "CAUTION" if score < 95 else "TARGET"

    recommendations = []
    if missing_score < 0.95:
        recommendations.append("Handle missing values.")
    if schema_score < 1.0:
        recommendations.append("Review schema inconsistencies.")
    if duplicate_score < 1.0:
        recommendations.append("Remove duplicate records.")
    if imbalance_score and imbalance_score < 0.6:
        recommendations.append("Address class imbalance.")

    return {
        "integrity_score": score,
        "alert_level": alert_level,
        "recommendations": recommendations,
        "missing_score": missing_score,
        "schema_score": schema_score,
        "duplicate_score": duplicate_score,
        "imbalance_score": imbalance_score,
        "missing_by_col": missing_by_col,
    }
