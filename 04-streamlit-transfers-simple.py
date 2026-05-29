#uv run streamlit run 04-streamlit-transfers-fancy.py

from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent

st.set_page_config(page_title="Transfers Browser", layout="wide")
st.title("Transfers Browser")

@st.cache_data
def load_data():
    df = pd.read_csv(
        APP_DIR / "data/transfers.csv",
        low_memory=False,
        parse_dates=["transfer_date_parsed"],
        dtype={
            "consideration": "int64",
            "assessment_total": "int64",
        },
    )
    df["transfer_date_parsed"] = df["transfer_date_parsed"].dt.date
    df = df.sort_values("transfer_date_parsed", ascending=False)
    return df

df = load_data()

###
# Build the filters
###

st.sidebar.header("Filters")

dates = df["transfer_date_parsed"].dropna()
date_min = dates.min()
date_max = dates.max()

date_range = st.sidebar.slider(
    "Transfer date",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
)

transfer_types = ["All"] + sorted(df["transfer_description"].dropna().unique())
transfer_type = st.sidebar.selectbox("Transfer type", transfer_types)

grantor_search = st.sidebar.text_input("Grantor contains")
grantee_search = st.sidebar.text_input("Grantee contains")

# Filters

filtered = df[df["transfer_date_parsed"].between(date_range[0], date_range[1])]

if transfer_type != "All":
    filtered = filtered[filtered["transfer_description"] == transfer_type]

if grantor_search:
    grantor_matches = filtered["grantor"].str.contains(
        grantor_search, case=False, na=False, regex=False
    )
    filtered = filtered[grantor_matches]

if grantee_search:
    grantee_matches = filtered["grantee"].str.contains(
        grantee_search, case=False, na=False, regex=False
    )
    filtered = filtered[grantee_matches]

###
# Make three columns with summary metrics
###

median_price = filtered[filtered["consideration"] > 0]["consideration"].median()

col1, col2, col3 = st.columns(3)
col1.metric("Transfers", f"{len(filtered):,}")
col2.metric("Unique parcels", f"{filtered['parcel_id'].nunique():,}")
col3.metric("Median non-zero price", f"${median_price:,.0f}")

###
# Show the filtered records
### 

st.subheader("Records")

columns_to_show = [
    "transfer_date_parsed",
    "parcel_id",
    "grantor",
    "grantee",
    "consideration",
    "transfer_description",
    "physical_address",
    "city_state",
    "assessment_total",
]

records = filtered[columns_to_show]

st.dataframe(
    records,
    column_config={
        "assessment_total": st.column_config.NumberColumn(
            "assessment_total",
            format="$,%d",
        ),
        "consideration": st.column_config.NumberColumn(
            "consideration",
            format="$,%d",
        )
    },
    width="stretch",
    height=600,
)

st.download_button(
    "Download filtered rows",
    filtered.to_csv(index=False).encode("utf-8"),
    "filtered_transfers.csv",
    "text/csv",
)
