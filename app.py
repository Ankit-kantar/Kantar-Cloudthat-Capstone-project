import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Property Investment Insights",
    layout="wide"
)

# -------------------------------------------------
# Load data (cached for performance)
# -------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("final_property_data.csv")

df = load_data()

# -------------------------------------------------
# Title & How-to section
# -------------------------------------------------
st.title("🏠 Property Investment Insights Dashboard")

st.markdown("""
### 👋 How to use this dashboard
- Use the **filters on the left** to explore specific ZIP codes, price ranges, and income levels  
- **KPIs update automatically** based on your selection  
- Hover over charts to see **property-level details**  
- Scroll down to explore **individual listings**
""")

st.markdown("---")

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------
st.sidebar.header("🔍 Filter Your View")
st.sidebar.caption(
    "Adjust filters below to analyze different neighborhoods and pricing scenarios."
)

# ZIP filter
zip_options = sorted(df['zip_code'].unique())
selected_zips = st.sidebar.multiselect(
    "Select ZIP Code(s)",
    options=zip_options,
    default=zip_options
)

# Listing price filter
price_min, price_max = int(df['listing_price'].min()), int(df['listing_price'].max())
selected_price = st.sidebar.slider(
    "Listing Price Range ($)",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, price_max)
)

# Median income filter
income_min, income_max = int(df['median_income'].min()), int(df['median_income'].max())
selected_income = st.sidebar.slider(
    "Median Income Range ($)",
    min_value=income_min,
    max_value=income_max,
    value=(income_min, income_max)
)

# -------------------------------------------------
# Apply filters
# -------------------------------------------------
filtered_df = df[
    (df['zip_code'].isin(selected_zips)) &
    (df['listing_price'].between(*selected_price)) &
    (df['median_income'].between(*selected_income))
]

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# -------------------------------------------------
# KPI Section
# -------------------------------------------------
st.markdown("## 📊 Key Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Avg Listing Price",
    f"${filtered_df['listing_price'].mean():,.0f}"
)

c2.metric(
    "Avg Price per Sq Ft",
    f"${filtered_df['price_per_sqft'].mean():,.0f}"
)

c3.metric(
    "Avg Median Income",
    f"${filtered_df['median_income'].mean():,.0f}"
)

c4.metric(
    "Avg School Rating",
    f"{filtered_df['school_rating'].mean():.1f}"
)

st.caption("📌 KPIs reflect averages based on your current filter selection.")

st.markdown("---")

# -------------------------------------------------
# Visualizations
# -------------------------------------------------
st.markdown("## 📈 Property Insights")

# School Rating vs Listing Price
fig_school_price = px.scatter(
    filtered_df,
    x="school_rating",
    y="listing_price",
    color="median_income",
    size="sq_ft",
    hover_data={
        "zip_code": True,
        "listing_price": ":,.0f",
        "sq_ft": True,
        "median_income": ":,.0f"
    },
    labels={
        "school_rating": "School Rating (1 = Low, 10 = High)",
        "listing_price": "Listing Price ($)",
        "median_income": "Median Income ($)"
    },
    title="💡 How School Quality Impacts Property Prices"
)

fig_school_price.update_layout(
    title_x=0.5,
    legend_title_text="Median Income"
)

st.plotly_chart(fig_school_price, use_container_width=True)

# Median Income vs Price per Sq Ft
fig_income_pps = px.scatter(
    filtered_df,
    x="median_income",
    y="price_per_sqft",
    color="school_rating",
    hover_data={
        "zip_code": True,
        "price_per_sqft": ":,.0f",
        "school_rating": True
    },
    labels={
        "median_income": "Median Household Income ($)",
        "price_per_sqft": "Price per Sq Ft ($)",
        "school_rating": "School Rating"
    },
    title="💰 Neighborhood Income vs Property Value (Price per Sq Ft)"
)

fig_income_pps.update_layout(title_x=0.5)

st.plotly_chart(fig_income_pps, use_container_width=True)

# Listing Price Distribution
fig_price_dist = px.histogram(
    filtered_df,
    x="listing_price",
    nbins=25,
    labels={"listing_price": "Listing Price ($)"},
    title="📊 Distribution of Property Listing Prices"
)

fig_price_dist.update_layout(
    title_x=0.5,
    yaxis_title="Number of Properties"
)

st.plotly_chart(fig_price_dist, use_container_width=True)

st.markdown("---")

# -------------------------------------------------
# Data Table
# -------------------------------------------------
st.markdown("### 🔍 Explore Individual Properties")
st.caption(
    "This table shows property-level details for deeper inspection."
)

st.dataframe(
    filtered_df[
        [
            "zip_code",
            "listing_price",
            "sq_ft",
            "price_per_sqft",
            "median_income",
            "school_rating"
        ]
    ].sort_values("listing_price", ascending=False),
    use_container_width=True
)
