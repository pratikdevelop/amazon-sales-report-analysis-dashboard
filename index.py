import streamlit as st
import pandas as pd
import plotly.express as px

# ───────────────────────────────────────────────
# Page config (looks nicer)
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="Amazon Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ───────────────────────────────────────────────
# Title & description
# ───────────────────────────────────────────────
st.title("🛒 Amazon Sale Report Dashboard")
st.markdown("Simple interactive dashboard for **Amazon Sale Report.csv**")

# ───────────────────────────────────────────────
# Load and cache data
# ───────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Amazon Sale Report.csv", low_memory=False)
    except:
        st.error("File 'Amazon Sale Report.csv' not found in current folder!")
        st.stop()

    # Quick cleaning (you can expand this part later)
    df = df.drop_duplicates()
    
    # Convert dates (very common column names in Amazon reports)
    date_cols = ['Date', 'date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Try to find amount / qty columns (names vary)
    possible_amount = ['Amount', 'amount', 'Sale Amount', 'Order Value']
    possible_qty    = ['Qty', 'Quantity', 'qty']
    
    amount_col = next((c for c in possible_amount if c in df.columns), None)
    qty_col    = next((c for c in possible_qty    if c in df.columns), None)
    
    if amount_col:
        df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
    
    return df, amount_col, qty_col


df, AMOUNT_COL, QTY_COL = load_data()

if df.empty:
    st.error("No data loaded. Check file path & format.")
    st.stop()


# ───────────────────────────────────────────────
# Sidebar – Filters
# ───────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    
    # Date range
    if 'Date' in df.columns and not df['Date'].isna().all():
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        
        date_range = st.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    
    # Category
    if 'Category' in df.columns:
        categories = ['All'] + sorted(df['Category'].dropna().unique().tolist())
        selected_cat = st.multiselect("Category", categories, default=['All'])
        if 'All' not in selected_cat:
            df = df[df['Category'].isin(selected_cat)]
    
    # Status
    if 'Status' in df.columns:
        statuses = ['All'] + sorted(df['Status'].dropna().unique().tolist())
        selected_status = st.multiselect("Order Status", statuses, default=['All'])
        if 'All' not in selected_status:
            df = df[df['Status'].isin(selected_status)]
    
    # Fulfilment (Fulfilled by Amazon / Merchant)
    if 'Fulfilment' in df.columns:
        ful = ['All'] + sorted(df['Fulfilment'].dropna().unique().tolist())
        selected_ful = st.multiselect("Fulfilment", ful, default=['All'])
        if 'All' not in selected_ful:
            df = df[df['Fulfilment'].isin(selected_ful)]


# ───────────────────────────────────────────────
# Key Metrics (KPIs)
# ───────────────────────────────────────────────
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_orders = len(df)
total_revenue = df[AMOUNT_COL].sum() if AMOUNT_COL else 0
avg_order_value = df[AMOUNT_COL].mean() if AMOUNT_COL else 0
total_qty = df[QTY_COL].sum() if QTY_COL else 0

with col1:
    st.metric("Total Orders", f"{total_orders:,}")
with col2:
    st.metric("Total Revenue", f"₹ {total_revenue:,.0f}" if total_revenue else "-")
with col3:
    st.metric("Avg Order Value", f"₹ {avg_order_value:,.0f}" if avg_order_value else "-")
with col4:
    st.metric("Total Units Sold", f"{total_qty:,}" if total_qty else "-")


# ───────────────────────────────────────────────
# Charts
# ───────────────────────────────────────────────
st.subheader("Visualizations")

tab1, tab2, tab3 = st.tabs(["Revenue by Category", "Orders by Date", "Top Products"])

with tab1:
    if 'Category' in df.columns and AMOUNT_COL:
        cat_rev = df.groupby('Category', as_index=False)[AMOUNT_COL].sum().sort_values(AMOUNT_COL, ascending=False)
        fig1 = px.bar(cat_rev.head(12), x='Category', y=AMOUNT_COL,
                      title="Revenue by Category (Top 12)",
                      color=AMOUNT_COL, color_continuous_scale='Blues')
        st.plotly_chart(fig1, width='stretch')
    else:
        st.info("Category or Amount column not found")

with tab2:
    if 'Date' in df.columns and AMOUNT_COL:
        daily = df.groupby(df['Date'].dt.date)[AMOUNT_COL].sum().reset_index()
        fig2 = px.line(daily, x='Date', y=AMOUNT_COL,
                       title="Daily Revenue Trend",
                       markers=True)
        st.plotly_chart(fig2, width='stretch')
    else:
        st.info("Date or Amount column not found")

with tab3:
    if 'SKU' in df.columns or 'Style' in df.columns:
        prod_col = 'SKU' if 'SKU' in df.columns else 'Style'
        top_prod = df.groupby(prod_col, as_index=False)[AMOUNT_COL].sum().sort_values(AMOUNT_COL, ascending=False).head(10)
        fig3 = px.bar(top_prod, x=prod_col, y=AMOUNT_COL,
                      title=f"Top 10 {prod_col} by Revenue",
                      color=AMOUNT_COL, color_continuous_scale='Greens')
        st.plotly_chart(fig3, width='stretch')
    else:
        st.info("No SKU / Style column found")


# Optional: raw data preview
with st.expander("See raw filtered data (click to expand)"):
    st.dataframe(df.head(1000))


st.markdown("---")
st.caption("Built with ❤️ using Streamlit • Refresh page to reload original data")