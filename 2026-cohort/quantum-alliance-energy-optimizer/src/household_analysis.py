"""
Household energy analysis pipeline.

This module aggregates appliance usage, calculates totals for energy,
cost, and carbon, compares against benchmarks, and attaches
efficiency scores.
"""

from src.database import (
    get_household,
    get_household_appliances,
    get_benchmark,
)

from src.energy_calculations import (
    calculate_daily_kwh,
    calculate_monthly_kwh,
    calculate_monthly_cost,
    calculate_carbon_footprint,
    calculate_benchmark_percentage,
)

from src.energy_efficiency import (
    calculate_efficiency_score,
    get_efficiency_label,
)


def analyze_household(household_id):
    """
    Perform a full energy analysis for a given household.

    Args:
        household_id (int): ID of the household to analyze.

    Returns:
        dict: Complete household analysis including:
              energy consumption,
              cost,
              carbon footprint,
              benchmark comparison,
              efficiency score,
              efficiency label,
              and appliance breakdown.
    """

    # ------------------------------------------------------------
    # Get household information
    # ------------------------------------------------------------

    household = get_household(household_id)

    if not household:
        return None

    # ------------------------------------------------------------
    # Get benchmark data for housing type
    # ------------------------------------------------------------

    benchmark = get_benchmark(household["housing_type"])

    if not benchmark:
        benchmark_kwh_monthly = None
    else:
        benchmark_kwh_monthly = benchmark["benchmark_kwh_monthly"]

    # ------------------------------------------------------------
    # Get appliances belonging to this household
    # ------------------------------------------------------------

    appliances = get_household_appliances(household_id)

    total_daily_kwh = 0.0
    appliance_analysis = []

    # ------------------------------------------------------------
    # Calculate energy consumption for each appliance
    # ------------------------------------------------------------

    for app_row in appliances:

        # Convert sqlite3.Row to a normal dictionary
        app = dict(app_row)

        # Use effective_wattage because it automatically accounts
        # for a household-specific wattage override when provided.
        daily_kwh = calculate_daily_kwh(
            app["effective_wattage"],
            app["appliance_quantity"],
            app["daily_usage_hours"],
        )

        monthly_kwh = calculate_monthly_kwh(daily_kwh)

        total_daily_kwh += daily_kwh

        appliance_analysis.append({
            "appliance_id": app["appliance_id"],
            "appliance_name": app["appliance_name"],
            "wattage": app["effective_wattage"],
            "quantity": app["appliance_quantity"],
            "daily_usage_hours": app["daily_usage_hours"],
            "daily_kwh": round(daily_kwh, 2),
            "monthly_kwh": round(monthly_kwh, 2),
            "energy_star_rated": app["energy_star_rated"],
        })

    # ------------------------------------------------------------
    # Calculate household-level totals
    # ------------------------------------------------------------

    total_monthly_kwh = calculate_monthly_kwh(total_daily_kwh)

    monthly_cost = calculate_monthly_cost(
        total_monthly_kwh,
        household["electricity_rate_per_kwh"],
    )

    monthly_carbon = calculate_carbon_footprint(
        total_monthly_kwh,
        household["carbon_emission_factor"],
    )

    # ------------------------------------------------------------
    # Compare household consumption with benchmark
    # ------------------------------------------------------------

    pct_vs_benchmark = calculate_benchmark_percentage(
        total_monthly_kwh,
        benchmark_kwh_monthly,
    )

    # ------------------------------------------------------------
    # Calculate efficiency score and label
    # ------------------------------------------------------------

    efficiency_score = calculate_efficiency_score(
        pct_vs_benchmark
    )

    efficiency_label = get_efficiency_label(
        efficiency_score
    )

    # ------------------------------------------------------------
    # Return complete analysis
    # ------------------------------------------------------------

    return {
        "household_id": household["household_id"],
        "housing_type": household["housing_type"],
        "apartment_size_category": household["apartment_size_category"],
        "electricity_rate_per_kwh": household["electricity_rate_per_kwh"],
        "carbon_emission_factor": household["carbon_emission_factor"],
        "benchmark_kwh_monthly": benchmark_kwh_monthly,
        "daily_kwh": round(total_daily_kwh, 2),
        "monthly_kwh": round(total_monthly_kwh, 2),
        "monthly_cost": round(monthly_cost, 2),
        "monthly_carbon_kg": round(monthly_carbon, 2),
        "pct_vs_benchmark": (
            round(pct_vs_benchmark, 2)
            if pct_vs_benchmark is not None
            else None
        ),
        "efficiency_score": efficiency_score,
        "efficiency_label": efficiency_label,
        "appliances": appliance_analysis,
    }