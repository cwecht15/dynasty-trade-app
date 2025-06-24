#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd



# In[ ]:


import pandas as pd
import streamlit as st

# Load and round data
df = pd.read_csv("C:/Users/cwech/Documents/Football/Final_Trade_Data.csv")
df['Trade Value'] = df['Trade Value'].round(1)
df['SF Trade Value'] = df['SF Trade Value'].round(1)

# Set page config
st.set_page_config(page_title="Dynasty Trade Value App", layout="centered")
st.title("🏈 Dynasty Trade Analyzer")

# Select league format
format_type = st.radio("Select League Format", ["1-QB", "Superflex"])
value_column = "Trade Value" if format_type == "1-QB" else "SF Trade Value"

# Format label with team and position for players
def format_label(row):
    if pd.isna(row["POS"]):
        return row["Name"]  # For picks
    return f"{row['Name']} ({row['Team']} - {row['POS']})"

df["Display"] = df.apply(format_label, axis=1)

# Create reusable function to select assets for each team
def asset_selector(label, key_prefix):
    st.subheader(label)
    assets = []
    i = 0
    while True:
        selected = st.selectbox(
            f"Select asset {i + 1}",
            [""] + df["Display"].tolist(),
            key=f"{key_prefix}_{i}",
        )
        if selected:
            assets.append(selected)
            i += 1
        else:
            break
    return assets

# Select assets for each team
team_a_assets = asset_selector("Team A Assets", "a")
team_b_assets = asset_selector("Team B Assets", "b")

# Helper to calculate value sum
def calculate_total(selected_assets):
    rows = df[df["Display"].isin(selected_assets)]
    return rows[value_column].sum(), rows[[value_column, "Display"]]

# Calculate and display values
team_a_total, team_a_table = calculate_total(team_a_assets)
team_b_total, team_b_table = calculate_total(team_b_assets)

st.markdown("### Trade Summary")

col1, col2 = st.columns(2)
with col1:
    st.write("**Team A Total Value:**", team_a_total)
    st.dataframe(team_a_table.rename(columns={"Display": "Asset", value_column: "Value"}), use_container_width=True)
with col2:
    st.write("**Team B Total Value:**", team_b_total)
    st.dataframe(team_b_table.rename(columns={"Display": "Asset", value_column: "Value"}), use_container_width=True)

# Summary difference
st.markdown("---")
if team_a_total > team_b_total:
    st.success(f"✅ Team A is giving up **{team_a_total - team_b_total:.1f}** more in value.")
elif team_b_total > team_a_total:
    st.success(f"✅ Team B is giving up **{team_b_total - team_a_total:.1f}** more in value.")
else:
    st.info("♻️ This trade is perfectly balanced.")

