import pandas as pd
import streamlit as st
import textwrap
from src.utils.helpers import detect_column, normalize_text, extract_rule_fields

def find_matching_body_rule(df, torso_value, body_value):
    if df is None or df.empty:
        return None
        
    torso_col = detect_column(df, ["Torso Length", "torso", "torso length"])
    shape_col = detect_column(df, ["Body Proportion", "Body Shape", "body shape", "shape"])

    if torso_col and shape_col:
        matched = df[
            (df[torso_col].astype(str) == str(torso_value)) &
            (df[shape_col].astype(str) == str(body_value))
        ]
        if not matched.empty:
            return matched.iloc[0]
    return None

def filter_profile_by_season(profile_df, season):
    if profile_df is None or profile_df.empty:
        return pd.DataFrame()
        
    season_col = detect_column(profile_df, ["season", "Season", "personal_color", "palette season"])
    if season_col is None:
        return pd.DataFrame()
    return profile_df[profile_df[season_col].astype(str).str.lower() == season.lower()]

def render_profile_info(profile_df, season):
    filtered = filter_profile_by_season(profile_df, season)
    if filtered.empty:
        st.markdown(
            """
            <div class="beauty-tip">
                Chưa tìm thấy thông tin tương ứng trong file personal_color_profiles.csv.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    row = filtered.iloc[0]
    shown = 0
    for col in filtered.columns:
        if str(col).strip().lower() == "season":
            continue
        value = normalize_text(row[col])
        if value:
            st.markdown(
                f"""
                <div class="beauty-tip">
                    <b>{col}:</b><br>{value}
                </div>
                """,
                unsafe_allow_html=True
            )
            shown += 1
        if shown >= 6:
            break
