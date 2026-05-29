#uv run streamlit run 04-streamlit-transfers-simple.py

from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent


st.set_page_config(page_title="Spotsylvania Transfers", layout="wide")
st.title("Spotsylvania Property Transfers")


@st.cache_data
def load_data():
    df = pd.read_csv(
        APP_DIR / "data/transfers.csv",
        low_memory=False,
        parse_dates=["transfer_date_parsed"],
        dtype={
            "consideration": "float64",
            "assessment_total": "float64",
            "assessment_land": "float64",
            "assessment_building": "float64",
            "assessment_improvements": "float64",
            "acreage": "float64",
        },
    )
    df["transfer_date_parsed"] = df["transfer_date_parsed"].dt.date
    return df.sort_values("transfer_date_parsed", ascending=False)


def top_table(df, group_column):
    return (
        df.dropna(subset=[group_column])
        .groupby(group_column)
        .agg(
            transfers=("parcel_id", "size"),
            unique_parcels=("parcel_id", "nunique"),
            total_consideration=("consideration", "sum"),
            median_consideration=("consideration", "median"),
            total_assessment=("assessment_total", "sum"),
        )
        .sort_values(["transfers", "total_consideration"], ascending=False)
        .head(25)
    )


money_columns = {
    "consideration": st.column_config.NumberColumn("consideration", format="$%,.0f"),
    "assessment_total": st.column_config.NumberColumn(
        "assessment_total",
        format="$%,.0f",
    ),
    "assessment_land": st.column_config.NumberColumn(
        "assessment_land",
        format="$%,.0f",
    ),
    "assessment_building": st.column_config.NumberColumn(
        "assessment_building",
        format="$%,.0f",
    ),
    "assessment_improvements": st.column_config.NumberColumn(
        "assessment_improvements",
        format="$%,.0f",
    ),
    "total_consideration": st.column_config.NumberColumn(
        "total_consideration",
        format="$%,.0f",
    ),
    "median_consideration": st.column_config.NumberColumn(
        "median_consideration",
        format="$%,.0f",
    ),
    "total_assessment": st.column_config.NumberColumn(
        "total_assessment",
        format="$%,.0f",
    ),
}


df = load_data()

dates = df["transfer_date_parsed"].dropna()
consideration = df["consideration"].dropna()
assessment = df["assessment_total"].dropna()

st.sidebar.header("Filters")

date_range = st.sidebar.slider(
    "Transfer date",
    min_value=dates.min(),
    max_value=dates.max(),
    value=(dates.min(), dates.max()),
)

transfer_types = sorted(df["transfer_description"].dropna().unique())
selected_transfer_types = st.sidebar.multiselect("Transfer type", transfer_types)

cities = sorted(df["city_state"].dropna().unique())
selected_cities = st.sidebar.multiselect("City/state", cities)

consideration_range = st.sidebar.slider(
    "Consideration",
    min_value=int(consideration.min()),
    max_value=int(consideration.max()),
    value=(int(consideration.min()), int(consideration.max())),
    step=10_000,
)

assessment_range = st.sidebar.slider(
    "Total assessment",
    min_value=int(assessment.min()),
    max_value=int(assessment.max()),
    value=(int(assessment.min()), int(assessment.max())),
    step=10_000,
)

only_nonzero = st.sidebar.checkbox("Only nonzero consideration")

st.sidebar.subheader("Text search")
grantor_search = st.sidebar.text_input("Grantor contains")
grantee_search = st.sidebar.text_input("Grantee contains")
record_search = st.sidebar.text_input("Parcel, address, legal description, instrument")

filtered = df[df["transfer_date_parsed"].between(date_range[0], date_range[1])]

if selected_transfer_types:
    filtered = filtered[filtered["transfer_description"].isin(selected_transfer_types)]

if selected_cities:
    filtered = filtered[filtered["city_state"].isin(selected_cities)]

filtered = filtered[
    filtered["consideration"].between(consideration_range[0], consideration_range[1])
    & filtered["assessment_total"].between(assessment_range[0], assessment_range[1])
]

if only_nonzero:
    filtered = filtered[filtered["consideration"] > 0]

grantor_search = grantor_search.strip()
if grantor_search:
    filtered = filtered[
        filtered["grantor"].str.contains(
            grantor_search,
            case=False,
            na=False,
            regex=False,
        )
    ]

grantee_search = grantee_search.strip()
if grantee_search:
    filtered = filtered[
        filtered["grantee"].str.contains(
            grantee_search,
            case=False,
            na=False,
            regex=False,
        )
    ]

record_search = record_search.strip()
if record_search:
    search_columns = [
        "parcel_id",
        "physical_address",
        "street_name",
        "legal_description_1",
        "legal_description_2",
        "instrument_id",
    ]
    matches = pd.Series(False, index=filtered.index)
    for column in search_columns:
        matches = matches | filtered[column].astype(str).str.contains(
            record_search,
            case=False,
            na=False,
            regex=False,
        )
    filtered = filtered[matches]

sales = filtered[filtered["transfer_description"] == "Sale"]
nonzero_prices = filtered[filtered["consideration"] > 0]["consideration"]
sales_with_prices = sales[
    (sales["consideration"] > 0) & (sales["assessment_total"] > 0)
]

if filtered.empty:
    st.warning("No rows match the current filters.")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Transfers", f"{len(filtered):,}")
col2.metric("Unique parcels", f"{filtered['parcel_id'].nunique():,}")
col3.metric("Total consideration", f"${filtered['consideration'].sum():,.0f}")
col4.metric(
    "Median nonzero price",
    "-" if nonzero_prices.empty else f"${nonzero_prices.median():,.0f}",
)
col5.metric("Sales", f"{len(sales):,}")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total assessed value", f"${filtered['assessment_total'].sum():,.0f}")
col2.metric("Median assessment", f"${filtered['assessment_total'].median():,.0f}")
median_sale_ratio = (
    sales_with_prices["consideration"] / sales_with_prices["assessment_total"]
).median()
col3.metric(
    "Median sale/assessment",
    "-" if pd.isna(median_sale_ratio) else f"{median_sale_ratio:.2f}x",
)
col4.metric("Unique grantors", f"{filtered['grantor'].nunique():,}")
col5.metric("Unique grantees", f"{filtered['grantee'].nunique():,}")

overview_tab, breakdowns_tab, records_tab, sources_tab = st.tabs(
    ["Overview", "Breakdowns", "Records", "Sources"]
)

with overview_tab:
    st.subheader("Transfers by Month")
    monthly = (
        filtered.assign(
            month=pd.to_datetime(filtered["transfer_date_parsed"])
            .dt.to_period("M")
            .astype(str)
        )
        .groupby("month")
        .size()
        .rename("transfers")
    )
    st.line_chart(monthly, height=260)

    st.subheader("Dollars by Year")
    yearly = (
        filtered.groupby("transfer_year")[["consideration", "assessment_total"]]
        .sum()
        .sort_index()
    )
    st.bar_chart(yearly, height=260)

    left, right = st.columns(2)
    with left:
        st.subheader("Top Transfer Types")
        st.dataframe(
            top_table(filtered, "transfer_description"),
            column_config=money_columns,
            width="stretch",
        )
    with right:
        st.subheader("Top Cities")
        st.dataframe(
            top_table(filtered, "city_state"),
            column_config=money_columns,
            width="stretch",
        )

with breakdowns_tab:
    group_column = st.selectbox(
        "Group rows by",
        [
            "transfer_description",
            "transfer_code",
            "city_state",
            "street_name",
            "grantor",
            "grantee",
            "source_year",
            "source_title",
            "acreage_units",
        ],
    )
    grouped = top_table(filtered, group_column)
    st.dataframe(grouped, column_config=money_columns, width="stretch", height=520)
    st.bar_chart(grouped["transfers"], height=260)

with records_tab:
    st.subheader("Filtered Records")

    default_columns = [
        "transfer_date_parsed",
        "parcel_id",
        "grantor",
        "grantee",
        "consideration",
        "transfer_description",
        "physical_address",
        "city_state",
        "assessment_total",
        "acreage",
        "acreage_units",
        "source_title",
        "source_url",
    ]
    selected_columns = st.multiselect(
        "Columns",
        df.columns,
        default=default_columns,
    )
    if not selected_columns:
        selected_columns = default_columns
    sort_column = st.selectbox("Sort by", selected_columns)
    sort_descending = st.checkbox("Sort descending", value=True)

    records = filtered[selected_columns].sort_values(
        sort_column,
        ascending=not sort_descending,
    )
    st.dataframe(
        records,
        column_config=money_columns,
        width="stretch",
        height=560,
    )

    st.download_button(
        "Download filtered rows",
        filtered.to_csv(index=False).encode("utf-8"),
        "filtered_transfers.csv",
        "text/csv",
    )

with sources_tab:
    source_columns = [
        "source_document_id",
        "source_title",
        "source_url",
        "source_period_type",
        "source_year",
        "source_start_month",
        "source_end_month",
        "source_schema",
    ]
    sources = (
        filtered[source_columns]
        .drop_duplicates()
        .sort_values(["source_year", "source_start_month", "source_title"])
    )
    st.dataframe(sources, width="stretch", height=520)
