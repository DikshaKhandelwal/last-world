from __future__ import annotations

import io
import json
import pandas as pd


def parse_input(raw: str) -> pd.DataFrame:
    raw = raw.strip()
    if raw.startswith('[') or raw.startswith('{'):
        data = json.loads(raw)
        return pd.DataFrame(data)
    if '\t' in raw:
        return pd.read_csv(io.StringIO(raw), sep='\t')
    return pd.read_csv(io.StringIO(raw))


def statistical_profile(df: pd.DataFrame) -> dict:
    profile = {}
    for col in df.columns:
        series = df[col]
        profile[col] = {
            'dtype': str(series.dtype),
            'min': series.min() if pd.api.types.is_numeric_dtype(series) else None,
            'max': series.max() if pd.api.types.is_numeric_dtype(series) else None,
            'mean': float(series.mean()) if pd.api.types.is_numeric_dtype(series) else None,
            'std': float(series.std()) if pd.api.types.is_numeric_dtype(series) else None,
            'null_count': int(series.isna().sum()),
            'unique_count': int(series.nunique()),
            'top_values': series.value_counts().head(3).to_dict(),
        }
    return profile


def detect_anomalies(df: pd.DataFrame, profile: dict) -> list[dict]:
    flags = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            mean = df[col].mean()
            std = df[col].std()
            if std and std > 0:
                for idx, value in df[col].items():
                    if abs(value - mean) > 3 * std:
                        flags.append({'row': int(idx), 'column': col, 'value': value, 'flag_type': 'OUTLIER', 'severity': 'high'})
        if df[col].nunique() == 1:
            flags.append({'row': None, 'column': col, 'value': df[col].iloc[0], 'flag_type': 'UNIFORM', 'severity': 'medium'})
    return flags


def detect_impossible_values(df: pd.DataFrame) -> list[dict]:
    flags: list[dict] = []
    for col in df.columns:
        lowered = col.lower()
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        for idx, value in df[col].items():
            if 'age' in lowered and (value < 0 or value > 120):
                flags.append({'row': int(idx), 'column': col, 'value': value, 'flag_type': 'IMPOSSIBLE_VALUE', 'severity': 'high'})
            if any(key in lowered for key in ['pct', 'percent']) and (value < 0 or value > 100):
                flags.append({'row': int(idx), 'column': col, 'value': value, 'flag_type': 'IMPOSSIBLE_VALUE', 'severity': 'high'})
            if any(key in lowered for key in ['temp', 'temperature']) and (value < -80 or value > 80):
                flags.append({'row': int(idx), 'column': col, 'value': value, 'flag_type': 'IMPOSSIBLE_VALUE', 'severity': 'high'})
    return flags
