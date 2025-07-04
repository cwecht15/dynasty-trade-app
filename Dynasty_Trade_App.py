#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd


# Read into DataFrames
df_values = pd.read_csv("Dynasty_Values.csv")
df_picks = pd.read_csv("Dynasty_Pick_Values.csv")
df_overall = pd.read_csv("OverallDynastyRankings.csv")
df_superflex = pd.read_csv("SuperflexDynastyRankings.csv")

# Preview
print(df_values.head())
print(df_picks.head())
print(df_overall.head())
print(df_superflex.head())


# In[7]:


# Merge df_overall with df_values on RANK
df_overall_merged = df_overall.merge(
    df_values[['RANK', 'Trade Value']], 
    on='RANK', 
    how='left'
)

# Merge df_superflex with df_values on RANK, keeping Trade Value SF from df_superflex
df_superflex_merged = df_superflex.merge(
    df_values[['RANK','SF Trade Value']],  # Only join on the rank without bringing in 'Trade Value'
    on='RANK', 
    how='left'
)

# Preview results
df_overall_merged.head()
df_superflex_merged.head()


# In[10]:


# Merge on Player, Team, and Position
df_combined = df_overall_merged.merge(
    df_superflex_merged,
    on=['Name', 'Team', 'POS'],
    suffixes=('_overall', '_sf'),
    how='outer'  # Use 'outer' if you want to keep all players from both datasets
)

# Preview the merged DataFrame
df_combined.head()


# In[12]:


# Select only the desired columns
df_final = df_combined[[
    'Name',        # Name
    'POS',      # POS
    'Team',
    'Age_overall',   # From df_overall_merged
    'Trade Value',   # From df_overall_merged
    'SF Trade Value' # From df_superflex_merged
]]

# Optionally rename columns for clarity
df_final = df_final.rename(columns={
    'Player': 'Name',
    'Position': 'POS',
    'Age_overall': 'Age'
})

# Preview the final DataFrame
print(df_final.head())


# In[14]:


# Prepare the pick DataFrame to match the structure of df_final
df_picks_prepped = df_picks.rename(columns={
    'Pick': 'Name',              # Align with Name column
    'Trade Value': 'Trade Value',
    'SF Trade Value': 'SF Trade Value'
})

# Add missing columns with NaN
df_picks_prepped['POS'] = pd.NA
df_picks_prepped['Team'] = pd.NA
df_picks_prepped['Age'] = pd.NA

# Reorder columns to match df_final
df_picks_prepped = df_picks_prepped[[
    'Name', 'POS', 'Team', 'Age', 'Trade Value', 'SF Trade Value'
]]

# Append to the final player DataFrame
df_final_combined = pd.concat([df_final, df_picks_prepped], ignore_index=True)

# Preview the combined DataFrame
df_final_combined.tail()


# In[ ]:
import pandas as pd
import streamlit as st

# --- Load and clean data ---
df = pd.read_csv("Final_Trade_Data.csv")
df["Trade Value"] = df["Trade Value"].round(1)
df["SF Trade Value"] = df["SF Trade Value"].round(1)

# --- Format label with full info and integer/N/A age ---
def format_label(row):
    if pd.isna(row["POS"]):
        return row["Name"]
    
    if pd.isna(row["Age"]):
        age_str = "Age - N/A"
    else:
        age_str = f"Age - {int(round(row['Age']))}"
        
    return f"{row['Name']} ({row['Team']} - {row['POS']} - {age_str})"

df["Display"] = df.apply(format_label, axis=1)

# --- Streamlit UI setup ---
st.set_page_config(page_title="Dynasty Trade App", layout="centered")
st.title("🏈 Dynasty Trade Analyzer")

# League format selector
format_type = st.radio("Select League Format", ["1-QB", "Superflex"])
value_column = "Trade Value" if format_type == "1-QB" else "SF Trade Value"

# Team selectors
team_a_assets = st.multiselect(
    "Select assets for Team A",
    options=df["Display"].tolist(),
    default=st.session_state.get("team_a", []),
    key="team_a"
)

team_b_assets = st.multiselect(
    "Select assets for Team B",
    options=df["Display"].tolist(),
    default=st.session_state.get("team_b", []),
    key="team_b"
)

# --- Calculate totals (rounded values in table) ---
def calculate_total(assets):
    table = df[df["Display"].isin(assets)][["Display", value_column]].copy()
    table[value_column] = table[value_column].round(1)
    table["Value"] = table[value_column].map(lambda x: f"{x:.1f}")
    return table[value_column].sum(), table.rename(columns={"Display": "Asset"})[["Asset", "Value"]]

team_a_value, team_a_table = calculate_total(team_a_assets)
team_b_value, team_b_table = calculate_total(team_b_assets)

# --- Uneven player adjustment (rounded) ---
a_count = len(team_a_assets)
b_count = len(team_b_assets)

if a_count != b_count:
    diff = abs(a_count - b_count)
    adj = round(diff * 100, 1)
    if a_count < b_count:
        team_a_value += adj
        team_a_table.loc[len(team_a_table.index)] = ["Uneven Player Adjustment", adj]
    else:
        team_b_value += adj
        team_b_table.loc[len(team_b_table.index)] = ["Uneven Player Adjustment", adj]

# --- Display results ---
st.markdown("---")
st.markdown("### 💰 Trade Summary")

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Team A Total Value:** {round(team_a_value, 1)}")
    st.table(team_a_table)

with col2:
    st.write(f"**Team B Total Value:** {round(team_b_value, 1)}")
    st.table(team_b_table)

# --- Verdict ---
st.markdown("---")
diff_val = round(abs(team_a_value - team_b_value), 1)
if team_a_value > team_b_value:
    st.success(f"✅ Team A is giving up **{diff_val}** more value.")
elif team_b_value > team_a_value:
    st.success(f"✅ Team B is giving up **{diff_val}** more value.")
else:
    st.info("♻️ This trade is perfectly balanced.")
