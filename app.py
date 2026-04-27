import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🚗 Vehicle Price Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
df = pd.read_excel("latest_data.xlsx")

# Clean data
df["On_Road_Price"] = pd.to_numeric(df["On_Road_Price"], errors="coerce")
df = df.dropna(subset=["On_Road_Price"])

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Advanced Filters")

# State filter
state = st.sidebar.selectbox("Select State", sorted(df["State"].dropna().unique()))
filtered_df = df[df["State"] == state]

# OEM filter
oem = st.sidebar.selectbox("Select OEM", sorted(filtered_df["OEM_name"].dropna().unique()))
filtered_df = filtered_df[filtered_df["OEM_name"] == oem]

# Model filter
model = st.sidebar.selectbox("Select Model", sorted(filtered_df["Model_Name"].dropna().unique()))
filtered_df = filtered_df[filtered_df["Model_Name"] == model]

# Search
# search = st.sidebar.text_input("🔎 Search Variant")
# if search:
#     filtered_df = filtered_df[
#         filtered_df["Variant"].str.contains(search, case=False, na=False)
#     ]
variants = st.sidebar.multiselect(
    "Select Variant(s)",
    sorted(filtered_df["Variant"].dropna().unique())
)

if variants:
    filtered_df = filtered_df[filtered_df["Variant"].isin(variants)]

# Price range slider
# min_price = int(df["On_Road_Price"].min())
# max_price = int(df["On_Road_Price"].max())

# price_range = st.sidebar.slider(
#     "💰 Select Price Range",
#     min_price,
#     max_price,
#     (min_price, max_price),
# )

# filtered_df = filtered_df[
#     (filtered_df["On_Road_Price"] >= price_range[0]) &
#     (filtered_df["On_Road_Price"] <= price_range[1])
# ]
min_price = int(filtered_df["On_Road_Price"].min())
max_price = int(filtered_df["On_Road_Price"].max())

price_range = st.sidebar.slider(
    "💰 Select Price Range",
    min_price,
    max_price,
    (min_price, max_price),
)

filtered_df = filtered_df[
    (filtered_df["On_Road_Price"] >= price_range[0]) &
    (filtered_df["On_Road_Price"] <= price_range[1])
]

# ---------------- MAIN TITLE ----------------
st.title("🚀 Premium Vehicle Price Analytics Dashboard")

# ---------------- KPI CARDS ----------------
col1, col2, col3 = st.columns(3)

avg_price = int(filtered_df["On_Road_Price"].mean()) if not filtered_df.empty else 0
min_price_val = int(filtered_df["On_Road_Price"].min()) if not filtered_df.empty else 0
max_price_val = int(filtered_df["On_Road_Price"].max()) if not filtered_df.empty else 0

col1.metric("💰 Avg Price", f"₹ {avg_price:,}")
col2.metric("📉 Min Price", f"₹ {min_price_val:,}")
col3.metric("📈 Max Price", f"₹ {max_price_val:,}")

st.markdown("---")

# ---------------- INSIGHTS ----------------
st.subheader("🧠 Smart Insights")

if not filtered_df.empty:
    cheapest = filtered_df.loc[filtered_df["On_Road_Price"].idxmin()]
    expensive = filtered_df.loc[filtered_df["On_Road_Price"].idxmax()]

    st.success(f"💡 Cheapest Variant: {cheapest['Variant']} at ₹ {int(cheapest['On_Road_Price']):,}")
    st.warning(f"💡 Most Expensive Variant: {expensive['Variant']} at ₹ {int(expensive['On_Road_Price']):,}")
else:
    st.error("No data available for selected filters")

# ---------------- CHARTS ----------------
col1, col2 = st.columns(2)

# Variant price chart
with col1:
    st.subheader("🎨 Variant Price Comparison")
    if not filtered_df.empty:
        fig1 = px.bar(
            filtered_df,
            x="Variant",
            y="On_Road_Price",
            color="Variant",
            title="Price by Variant",
        )
        st.plotly_chart(fig1, use_container_width=True)

# OEM comparison
with col2:
    st.subheader("🏭 OEM Price Distribution")
    state_df = df[df["State"] == state]

    fig2 = px.box(
        state_df,
        x="OEM_name",
        y="On_Road_Price",
        color="OEM_name",
        title="OEM Comparison",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- MODEL COMPARISON ----------------
st.subheader("📊 Model Price Comparison")

model_df = (
    df[df["State"] == state]
    .groupby("Model_Name")["On_Road_Price"]
    .mean()
    .reset_index()
)

fig3 = px.bar(
    model_df,
    x="Model_Name",
    y="On_Road_Price",
    color="Model_Name",
    title="Average Price by Model",
)

st.plotly_chart(fig3, use_container_width=True)

# ---------------- TOP VEHICLES ----------------
st.subheader("🏆 Top 5 Expensive Vehicles")

top5 = df.sort_values(by="On_Road_Price", ascending=False).head(5)
st.dataframe(top5)

# ---------------- RAW DATA ----------------
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered_df)