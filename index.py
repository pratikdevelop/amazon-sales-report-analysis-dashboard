import streamlit as st
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go   # only needed if you later add custom traces

# ───────────────────────────────────────────────
# Page config
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="Amazon Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ───────────────────────────────────────────────
# Title & About
# ───────────────────────────────────────────────
st.title("🛒 Amazon Sale Report Dashboard")
st.markdown("""
### About this project
- Interactive analysis of Amazon India Sales Report  
- Built with: Streamlit • Pandas • Plotly  
- Features: filtering, KPIs, trends, top products, city revenue map  
- Created by Pratik
""")

# ───────────────────────────────────────────────
# Data loading & caching
# ───────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Amazon Sale Report.csv", low_memory=False)
    except:
        st.error("File 'Amazon Sale Report.csv' not found!")
        st.stop()

    df = df.drop_duplicates()
    
    # Date conversion
    date_cols = ['Date', 'date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Detect amount & quantity columns
    possible_amount = ['Amount', 'amount', 'Sale Amount', 'Order Value']
    possible_qty    = ['Qty', 'Quantity', 'qty']
    
    amount_col = next((c for c in possible_amount if c in df.columns), None)
    qty_col    = next((c for c in possible_qty    if c in df.columns), None)
    
    if amount_col:
        df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
    
    return df, amount_col, qty_col


@st.cache_data
def get_city_coords():
    # Extend this dictionary with more cities from your actual top cities
    return {
        'BENGALURU': (12.9716, 77.5946),
        'BANGALORE': (12.9716, 77.5946),
        'MUMBAI': (19.0760, 72.8777),
        'NEW DELHI': (28.6139, 77.2090),
        'DELHI': (28.6139, 77.2090),
        'HYDERABAD': (17.3850, 78.4867),
        'AHMEDABAD': (23.0225, 72.5714),
        'PUNE': (18.5204, 73.8567),
        'CHENNAI': (13.0827, 80.2707),
        'KOLKATA': (22.5726, 88.3639),
        'JAIPUR': (26.9124, 75.7873),
        'LUCKNOW': (26.8467, 80.9462),
        'SURAT': (21.1702, 72.8311),
        'KANPUR': (26.4499, 80.3319),
        'NAGPUR': (21.1458, 79.0882),
        # Add 20–50 more of your top cities for better coverage
    }


df, AMOUNT_COL, QTY_COL = load_data()

if df.empty or AMOUNT_COL is None:
    st.error("No data or revenue column found. Check file format.")
    st.stop()


# ───────────────────────────────────────────────
# Sidebar filters
# ───────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    
    if 'Date' in df.columns and not df['Date'].isna().all():
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    
    if 'Category' in df.columns:
        cats = ['All'] + sorted(df['Category'].dropna().unique().tolist())
        sel_cats = st.multiselect("Category", cats, default=['All'])
        if 'All' not in sel_cats:
            df = df[df['Category'].isin(sel_cats)]
    
    if 'Status' in df.columns:
        stats = ['All'] + sorted(df['Status'].dropna().unique().tolist())
        sel_stats = st.multiselect("Order Status", stats, default=['All'])
        if 'All' not in sel_stats:
            df = df[df['Status'].isin(sel_stats)]
    
    if 'Fulfilment' in df.columns:
        fulfils = ['All'] + sorted(df['Fulfilment'].dropna().unique().tolist())
        sel_ful = st.multiselect("Fulfilment", fulfils, default=['All'])
        if 'All' not in sel_ful:
            df = df[df['Fulfilment'].isin(sel_ful)]


# ───────────────────────────────────────────────
# KPIs
# ───────────────────────────────────────────────
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_orders = len(df)
total_revenue = df[AMOUNT_COL].sum() if AMOUNT_COL else 0
avg_order_value = df[AMOUNT_COL].mean() if AMOUNT_COL else 0
total_qty = df[QTY_COL].sum() if QTY_COL else 0

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Total Revenue", f"₹ {total_revenue:,.0f}" if total_revenue else "-")
col3.metric("Avg Order Value", f"₹ {avg_order_value:,.0f}" if avg_order_value else "-")
col4.metric("Total Units Sold", f"{total_qty:,}" if total_qty else "-")


# ───────────────────────────────────────────────
# Visualizations – Tabs
# ───────────────────────────────────────────────
st.subheader("Visualizations")

tab1, tab2, tab3, tab4 = st.tabs([
    "Revenue by Category",
    "Revenue Trend",
    "Top Products",
    "City Revenue Map"
])

with tab1:
    if 'Category' in df.columns and AMOUNT_COL:
        cat_rev = df.groupby('Category', as_index=False)[AMOUNT_COL].sum().sort_values(AMOUNT_COL, ascending=False)
        fig1 = px.bar(
            cat_rev.head(12),
            x='Category',
            y=AMOUNT_COL,
            title="Top 12 Categories by Revenue",
            color=AMOUNT_COL,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Category or Amount column missing")

with tab2:
    if 'Date' in df.columns and AMOUNT_COL:
        daily = df.groupby(df['Date'].dt.date)[AMOUNT_COL].sum().reset_index()
        fig2 = px.line(
            daily,
            x='Date',
            y=AMOUNT_COL,
            title="Daily Revenue Trend",
            markers=True
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Date or Amount column missing")

with tab3:
    if 'SKU' in df.columns or 'Style' in df.columns:
        prod_col = 'SKU' if 'SKU' in df.columns else 'Style'
        top_prod = df.groupby(prod_col, as_index=False)[AMOUNT_COL].sum().sort_values(AMOUNT_COL, ascending=False).head(10)
        fig3 = px.bar(
            top_prod,
            x=prod_col,
            y=AMOUNT_COL,
            title=f"Top 10 {prod_col} by Revenue",
            color=AMOUNT_COL,
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No SKU or Style column found")

with tab4:
    st.subheader("Revenue by Shipping City – India")
    
    city_column = None
    for possible in ['ship-city', 'Ship-City', 'ship_city', 'Ship City']:
        if possible in df.columns:
            city_column = possible
            break
    
    if city_column and AMOUNT_COL:
        city_rev = df.groupby(city_column, as_index=False)[AMOUNT_COL].sum()
        city_rev = city_rev.rename(columns={AMOUNT_COL: 'Revenue', city_column: 'City'})
        city_rev = city_rev[city_rev['Revenue'] > 0]
        
        if city_rev.empty:
            st.info("No revenue data available after filtering")
        else:
            # Limit to top cities to avoid clutter + improve performance
            top_n = 150
            city_rev = city_rev.sort_values('Revenue', ascending=False).head(top_n)
            
            # Get coordinates
            city_coords = get_city_coords()
            
            # More flexible matching (upper case + strip)
            def get_lat(city):
                city_upper = str(city).strip().upper()
                coord = city_coords.get(city_upper)
                if coord:
                    return coord[0]
                # Optional: add fuzzy matching later if needed
                return None
            
            def get_lon(city):
                city_upper = str(city).strip().upper()
                coord = city_coords.get(city_upper)
                if coord:
                    return coord[1]
                return None
            
            city_rev['lat'] = city_rev['City'].apply(get_lat)
            city_rev['lon'] = city_rev['City'].apply(get_lon)
            
            # Cities with coordinates
            mapped = city_rev.dropna(subset=['lat', 'lon'])
            
            if mapped.empty:
                st.warning("None of the top cities matched our coordinate list")
                st.dataframe(city_rev.head(30).style.format({'Revenue': '{:,.0f}'}))
            else:
                fig_map = px.scatter_mapbox(
                    mapped,
                    lat='lat',
                    lon='lon',
                    hover_name='City',
                    hover_data={'Revenue': ':,.0f', 'lat': False, 'lon': False},
                    size='Revenue',
                    color='Revenue',
                    color_continuous_scale='Viridis',
                    size_max=55,
                    zoom=4,
                    title=f"Top {len(mapped)} Cities by Revenue (Bubble size = Revenue)",
                    mapbox_style="carto-positron",
                )
                
                fig_map.update_layout(
                    mapbox=dict(
                        center=dict(lat=20.6, lon=79.0),
                        zoom=4.0
                    ),
                    height=650,
                    margin={"r":0, "t":50, "l":0, "b":0}
                )
                
                st.plotly_chart(fig_map, use_container_width=True)
                
                unmatched = len(city_rev) - len(mapped)
                if unmatched > 0:
                    st.caption(f"Showing {len(mapped)} cities with coordinates • {unmatched} top cities not mapped")
    else:
        st.warning(f"No city column found (tried: ship-city, Ship-City, etc.). Available columns: {df.columns.tolist()}")


# ───────────────────────────────────────────────
# Raw data preview
# ───────────────────────────────────────────────
with st.expander("View first 1000 rows of filtered data"):
    st.dataframe(df.head(1000))

st.markdown("---")
st.caption("Built with ❤️ using Streamlit • Data from Amazon Sale Report • Refresh to reload")