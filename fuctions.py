"""
---------------------------------------------------------
AgriFlow - AI Powered Crop Distribution Optimizer

This file contains all the AI logic used in the project.

Workflow
--------
1. Load crop dataset
2. Filter data according to source city & crop
3. Calculate AI recommendation score
4. Allocate quantity among destination cities
5. Calculate expected profit
6. Calculate crop spoilage
7. Return final distribution table

---------------------------------------------------------
"""

# ============================================================
# IMPORTS
# ============================================================

# Import dataset loader
from data.data import load_data

# Pandas is used for dataframe operations
import pandas as pd


# ============================================================
# CALCULATE AI SCORE
# ============================================================
def calculate_score(df):
    """
    Calculates a recommendation score for every destination city.

    Higher score means the city is a better destination.

    Factors Used:
    -------------
    + High Demand
    + High Market Price
    + Large Population

    - High Supply
    - High Transport Cost
    """

    df = df.copy()

    df["score"] = (
        (df["demand_index"] * 40)
        + (df["market_price_per_kg"] * 0.5)
        + ((df["population"] / 1000000) * 5)
        - (df["supply_index"] * 20)
        - (df["transport_cost_per_kg"] * 2)
    )

    return df


# ============================================================
# ALLOCATE QUANTITY
# ============================================================
def allocate_quantity(df, quantity):
    """
    Distributes available crop quantity among cities
    according to their AI score.

    Example

    Total Score = 200

    Mumbai Score = 100

    Quantity = 1000 kg

    Allocation

    (100 / 200) * 1000

    = 500 kg
    """

    total_score = df["score"].sum()

    df["allocated_quantity"] = (
        (df["score"] / total_score)
        * quantity
    ).round(2)

    return df


# ============================================================
# CALCULATE PROFIT
# ============================================================
def calculate_profit(df):
    """
    Profit Formula

    Revenue
    =
    Allocated Quantity × Market Price

    Transport Cost
    =
    Allocated Quantity × Transport Cost

    Profit
    =
    Revenue - Transport Cost
    """

    revenue = (
        df["allocated_quantity"]
        * df["market_price_per_kg"]
    )

    transport = (
        df["allocated_quantity"]
        * df["transport_cost_per_kg"]
    )

    df["profit"] = (
        revenue - transport
    ).round(2)

    return df


# ============================================================
# CALCULATE SPOILAGE
# ============================================================
def calculate_waste(df):
    """
    Calculates crop spoilage.

    If travel time is within the safe transport limit,
    waste is considered zero.

    Otherwise

    Waste =
    Quantity × Spoilage Rate × Extra Hours
    """

    waste = []

    for _, row in df.iterrows():

        # Safe transportation
        if row["travel_time_hr"] <= row["max_transport_hours"]:
            waste.append(0)

        # Unsafe transportation
        else:

            extra_hours = (
                row["travel_time_hr"]
                - row["max_transport_hours"]
            )

            loss = (
                row["allocated_quantity"]
                * row["spoilage_rate_per_hour"]
                * extra_hours
            )

            waste.append(round(loss, 2))

    df["waste"] = waste

    return df


# ============================================================
# MAIN AI FUNCTION
# ============================================================
def generate_distribution(source_city, crop, quantity):
    """
    Main function used by app.py

    Inputs
    ------
    source_city
    crop
    quantity

    Returns
    -------
    DataFrame containing

    - AI Score
    - Allocated Quantity
    - Profit
    - Waste
    """

    # ----------------------------------------
    # Load dataset
    # ----------------------------------------
    df = load_data()

    # ----------------------------------------
    # Filter selected source city and crop
    # ----------------------------------------
    df = df[
        (df["source_city"] == source_city)
        &
        (df["crop"] == crop)
    ].copy()

    # ----------------------------------------
    # Calculate AI recommendation score
    # ----------------------------------------
    df = calculate_score(df)

    # ----------------------------------------
    # Allocate crop quantity
    # ----------------------------------------
    df = allocate_quantity(df, quantity)

    # ----------------------------------------
    # Calculate expected profit
    # ----------------------------------------
    df = calculate_profit(df)

    # ----------------------------------------
    # Calculate crop spoilage
    # ----------------------------------------
    df = calculate_waste(df)

    # ----------------------------------------
    # Sort cities by recommendation score
    # Highest score appears first
    # ----------------------------------------
    df = df.sort_values(
        by="score",
        ascending=False
    )

    # Reset dataframe indexing
    return df.reset_index(drop=True)