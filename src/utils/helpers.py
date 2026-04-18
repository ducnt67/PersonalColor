import pandas as pd

def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def detect_column(df, possible_names):
    if df is None or df.empty:
        return None
    lower_map = {str(col).strip().lower(): col for col in df.columns}
    for name in possible_names:
        key = name.strip().lower()
        if key in lower_map:
            return lower_map[key]
    return None

def extract_rule_fields(rule_row):
    if rule_row is None:
        return {}
    result = {}
    for col in rule_row.index:
        value = normalize_text(rule_row[col])
        if value:
            result[col] = value
    return result
