"""
Data profiling and anomaly detection utilities for CSV/JSON inputs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    report = {}
    for col in df.columns:
        series = df[col]
        dtype_actual = str(series.dtype)
        null_count = int(series.isnull().sum())
        null_pct = float(null_count) / max(len(series), 1)
        unique_count = int(series.nunique(dropna=True))
        value_range = None
        mean = None
        std_dev = None
        suspicious_values = []
        type_violations = []

        if pd.api.types.is_numeric_dtype(series):
            try:
                mean = float(series.mean())
                std_dev = float(series.std())
                value_range = [float(series.min()), float(series.max())]
                # suspicious values beyond 3 sigma
                if std_dev and not np.isnan(std_dev):
                    mu = mean
                    sigma = std_dev
                    outliers = series[(series - mu).abs() > 3 * sigma]
                    suspicious_values = outliers.dropna().tolist()
            except Exception:
                pass
        else:
            # Non-numeric heuristics
            pass

        report[col] = {
            'dtype_actual': dtype_actual,
            'null_count': null_count,
            'null_pct': null_pct,
            'unique_count': unique_count,
            'value_range': value_range,
            'mean': mean,
            'std_dev': std_dev,
            'suspicious_values': suspicious_values,
            'type_violations': type_violations
        }
    
    # Add duplicate row count and impossible combos placeholder
    report['_meta'] = {
        'duplicate_rows': int(df.duplicated().sum())
    }
    return report


def detect_impossible_combos(df: pd.DataFrame) -> List[Dict[str, Any]]:
    issues = []
    # Common impossible combos: end_date < start_date, percent > 100, age < 0
    if 'start_date' in df.columns and 'end_date' in df.columns:
        try:
            sd = pd.to_datetime(df['start_date'], errors='coerce')
            ed = pd.to_datetime(df['end_date'], errors='coerce')
            bad = df[(ed < sd) & (~ed.isnull()) & (~sd.isnull())]
            for idx in bad.index.tolist():
                issues.append({'row': int(idx), 'issue': 'end_date < start_date'})
        except Exception:
            pass

    if 'age' in df.columns:
        bad = df[df['age'] < 0]
        for idx in bad.index.tolist():
            issues.append({'row': int(idx), 'issue': 'age < 0'})

    # percent columns
    for col in df.columns:
        if col.lower().endswith('pct') or col.lower().endswith('percent'):
            bad = df[df[col] > 100]
            for idx in bad.index.tolist():
                issues.append({'row': int(idx), 'issue': f'{col} > 100'})

    return issues


def infer_column_domain(col_name: str, series: pd.Series) -> str:
    """Infer domain/type from column name and values."""
    name = col_name.lower()
    if 'age' in name:
        return 'age'
    if 'date' in name or 'time' in name:
        return 'datetime'
    if 'id' in name:
        return 'identifier'
    if 'lat' in name or 'lon' in name or 'latitude' in name:
        return 'geo'
    if series.dtype == 'O' and series.str.match(r'^[0-9\-]+$').any():
        return 'identifier'
    return 'unknown'
