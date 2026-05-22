import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales Intelligence Dashboard")
st.markdown("Understand your sales, profit and product performance in seconds")
st.markdown("---")

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_clean.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Profit Margin"] = df["Profit"] / df["Sales"]
    return df

df = load_data()

# -----------------------
# SIDEBAR FILTERS
# -----------------------
st.sidebar.title("Filters")

category_filter = st.sidebar.multiselect(
    "Select category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

min_date = df["Order Date"].min()
max_date = df["Order Date"].max()

date_range = st.sidebar.date_input(
    "Select date range",
    [min_date, max_date]
)

# -----------------------
# FILTER DATA
# -----------------------
filtered_df = df[
    (df["Order Date"] >= pd.Timestamp(date_range[0])) &
    (df["Order Date"] <= pd.Timestamp(date_range[1])) &
    (df["Category"].isin(category_filter))
]

# Safety check
if filtered_df.empty:
    st.warning("No data for selected filters")
    st.stop()

# -----------------------
# GLOBAL METRICS
# -----------------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
transactions = len(filtered_df)
profit_margin = total_profit / total_sales

product_profit = filtered_df.groupby("Product Name")["Profit"].sum()
best_product = product_profit.idxmax()
worst_product = product_profit.idxmin()

category_profit = filtered_df.groupby("Category")["Profit"].sum()
top_category = category_profit.idxmax()

sales_time = filtered_df.groupby("Order Date")["Sales"].sum().reset_index()

top_products = (
    filtered_df.groupby("Product Name")["Profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

# -----------------------
# TABS
# -----------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📈 Sales",
    "🛍️ Products",
    "📦 Categories",
    "💡 Insights"
])

# -----------------------
# TAB 1 - OVERVIEW
# -----------------------
with tab1:
    st.subheader("📊 Overview KPIs")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💰 Sales", f"${total_sales:,.0f}")
    c2.metric("📈 Profit", f"${total_profit:,.0f}")
    c3.metric("🧾 Transactions", transactions)
    c4.metric("📊 Margin", f"{profit_margin:.2%}")

# -----------------------
# TAB 2 - SALES
# -----------------------
with tab2:
    st.subheader("📈 Sales Over Time")

    fig = px.line(
        sales_time,
        x="Order Date",
        y="Sales",
        title="Sales Trend"
    )

    fig.update_traces(line_color="#4F8BF9")
    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TAB 3 - PRODUCTS
# -----------------------
with tab3:
    st.subheader("🛍️ Top Products")

    fig2 = px.bar(
        top_products,
        x="Product Name",
        y="Profit",
        color_discrete_sequence=["#00CC96"],
        title="Top Products by Profit"
    )

    fig2.update_layout(template="plotly_dark")

    st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# TAB 4 - CATEGORIES
# -----------------------
with tab4:
    st.subheader("📦 Category Performance")

    cat = filtered_df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()

    fig3 = px.pie(
        cat,
        names="Category",
        values="Profit",
        color_discrete_sequence=px.colors.sequential.Blues,
        title="Profit by Category"
    )

    fig3.update_layout(template="plotly_dark")

    st.plotly_chart(fig3, use_container_width=True)

# -----------------------
# TAB 5 - INSIGHTS
# -----------------------
with tab5:
    st.subheader("💡 Business Insights")

    c1, c2, c3 = st.columns(3)

    c1.success(f"🟢 Best product: {best_product}")
    c2.error(f"🔴 Worst product: {worst_product}")
    c3.info(f"📦 Top category: {top_category}")

    st.markdown("---")

    st.markdown(f"""
### 📊 Executive Summary

- Total Sales: ${total_sales:,.0f}  
- Total Profit: ${total_profit:,.0f}  
- Profit Margin: {profit_margin:.2%}  

👉 Main driver of revenue: **{top_category}**  
👉 Best product: **{best_product}**  
👉 Weakest product: **{worst_product}**
""")