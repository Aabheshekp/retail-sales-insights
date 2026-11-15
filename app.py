from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "sales.csv"
st.set_page_config(page_title="Retail Sales Insights", page_icon="📊", layout="wide")
st.title("Retail Sales Insights")
st.caption("Revenue, product mix, and regional trends from the included sample sales ledger.")

@st.cache_data
def load_data(file):
    df = pd.read_csv(file, parse_dates=["order_date"])
    required = {"order_date", "region", "category", "product", "quantity", "unit_price", "revenue", "customer_id"}
    missing = required - set(df.columns)
    if missing: raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    return df

upload = st.sidebar.file_uploader("Use another CSV", type="csv")
try:
    df = load_data(upload if upload else DATA)
except Exception as exc:
    st.error(f"Could not load sales data: {exc}"); st.stop()
regions = st.sidebar.multiselect("Regions", sorted(df.region.unique()), default=sorted(df.region.unique()))
categories = st.sidebar.multiselect("Categories", sorted(df.category.unique()), default=sorted(df.category.unique()))
start, end = st.sidebar.date_input("Order date range", (df.order_date.min().date(), df.order_date.max().date()))
filtered = df[df.region.isin(regions) & df.category.isin(categories) & df.order_date.dt.date.between(start, end)]
if filtered.empty: st.warning("No sales match these filters."); st.stop()
a,b,c,d = st.columns(4)
a.metric("Revenue", f"${filtered.revenue.sum():,.0f}")
b.metric("Orders", f"{len(filtered):,}")
c.metric("Units", f"{filtered.quantity.sum():,}")
d.metric("Customers", f"{filtered.customer_id.nunique():,}")
left,right = st.columns(2)
with left:
    st.subheader("Monthly revenue")
    monthly = filtered.set_index("order_date").resample("ME").revenue.sum()
    st.line_chart(monthly)
with right:
    st.subheader("Revenue by category")
    st.bar_chart(filtered.groupby("category").revenue.sum().sort_values(ascending=False))
st.subheader("Regional performance")
st.bar_chart(filtered.groupby("region").revenue.sum().sort_values(ascending=False))
st.subheader("Filtered transactions")
st.dataframe(filtered.sort_values("order_date", ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download filtered CSV", filtered.to_csv(index=False), "sales-filtered.csv", "text/csv")
