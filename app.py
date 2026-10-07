import streamlit as st
import plotly.express as px

# Import function to load dataset
from data.data import load_data

# Import AI recommendation function
from functions import generate_distribution


# =====================================================
# PAGE CONFIGURATION
# Sets the title, icon and page layout of the Streamlit app
# =====================================================
st.set_page_config(
    page_title="AgriFlow",
    page_icon="🌾",
    layout="wide"
)


# =====================================================
# CUSTOM CSS
# Adds a little styling to improve the UI appearance.
# Unsafe HTML is enabled because Streamlit allows CSS injection.
# =====================================================
st.markdown("""
<style>

.main{
    background-color:#f8f9fa;
}

.metric-card{
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 3px 12px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# LOAD DATASET
# Reads data.csv using load_data() function.
# This dataframe is used to populate dropdowns.
# =====================================================
df = load_data()


# =====================================================
# APP HEADER
# Display title and description of the project.
# =====================================================
st.title("🌾 AgriFlow")
st.subheader("AI Powered Crop Distribution Optimizer")

st.write("""
Distribute agricultural produce intelligently across multiple
cities by considering:

- 📈 Demand
- 💰 Market Price
- 🚚 Transport Cost
- ⏳ Travel Time
- 🌱 Crop Spoilage
""")

st.divider()


# =====================================================
# SIDEBAR
# Takes all user inputs.
# =====================================================
st.sidebar.header("Distribution Input")


# Select source city from available cities
source_city = st.sidebar.selectbox(
    "Source City",
    sorted(
        df["source_city"]
        .dropna()
        .astype(str)
        .unique()
    )
)


# Select crop from dataset
crop = st.sidebar.selectbox(
    "Crop",
    sorted(
        df["crop"]
        .dropna()
        .astype(str)
        .unique()
    )
)


# User enters available crop quantity
quantity = st.sidebar.number_input(
    "Available Quantity (kg)",
    min_value=100,
    value=1000,
    step=100
)


# Button to start AI recommendation
generate = st.sidebar.button(
    "🚚 Generate Distribution Plan",
    use_container_width=True
)


# =====================================================
# MAIN AI EXECUTION
# Runs only when button is pressed.
# =====================================================
if generate:

    # Generate AI based distribution plan
    result = generate_distribution(
        source_city,
        crop,
        quantity
    )

    # =================================================
    # KPI CALCULATIONS
    # Calculate values shown in dashboard cards.
    # =================================================

    # Total expected profit
    total_profit = result["profit"].sum()

    # Total estimated waste
    total_waste = result["waste"].sum()

    # Highest ranked destination city
    best_city = result.iloc[0]["destination_city"]

    # Total quantity distributed
    total_quantity = result["allocated_quantity"].sum()


    # =================================================
    # KPI DASHBOARD
    # Shows quick summary using Streamlit metric cards.
    # =================================================
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💰 Total Profit",
        f"₹{total_profit:,.0f}"
    )

    c2.metric(
        "🌱 Total Waste",
        f"{total_waste:.2f} kg"
    )

    c3.metric(
        "📦 Quantity Distributed",
        f"{total_quantity:.0f} kg"
    )

    c4.metric(
        "⭐ Best Destination",
        best_city
    )

    st.divider()


    # =================================================
    # DISTRIBUTION TABLE
    # Displays city-wise AI recommendation.
    # =================================================
    st.subheader("📋 AI Distribution Plan")

    display = result[
        [
            "destination_city",
            "allocated_quantity",
            "profit",
            "waste",
            "score"
        ]
    ]

    # Rename dataframe columns for better readability
    display.columns = [
        "Destination",
        "Allocated Quantity (kg)",
        "Expected Profit (₹)",
        "Waste (kg)",
        "AI Score"
    ]

    st.dataframe(
        display,
        use_container_width=True
    )

    st.divider()


    # =================================================
    # VISUAL ANALYTICS
    # Plotly charts for easier comparison.
    # =================================================

    col1, col2 = st.columns(2)


    # ---------------------------------------------
    # Pie Chart
    # Shows quantity allocated to each destination.
    # ---------------------------------------------
    with col1:

        st.subheader("📦 Quantity Distribution")

        pie = px.pie(
            result,
            names="destination_city",
            values="allocated_quantity",
            hole=0.45
        )

        st.plotly_chart(
            pie,
            use_container_width=True
        )


    # ---------------------------------------------
    # Profit Chart
    # Shows expected profit from every city.
    # ---------------------------------------------
    with col2:

        st.subheader("💰 Profit by City")

        bar = px.bar(
            result,
            x="destination_city",
            y="profit"
        )

        st.plotly_chart(
            bar,
            use_container_width=True
        )


    st.divider()


    # ---------------------------------------------
    # Waste Chart
    # Compares crop spoilage for each destination.
    # ---------------------------------------------
    st.subheader("🌱 Waste by City")

    waste_chart = px.bar(
        result,
        x="destination_city",
        y="waste"
    )

    st.plotly_chart(
        waste_chart,
        use_container_width=True
    )


# =====================================================
# DEFAULT SCREEN
# Displayed before user clicks the generate button.
# =====================================================
else:

    st.info(
        "👈 Select the crop and quantity from the sidebar and click **Generate Distribution Plan**."
    )