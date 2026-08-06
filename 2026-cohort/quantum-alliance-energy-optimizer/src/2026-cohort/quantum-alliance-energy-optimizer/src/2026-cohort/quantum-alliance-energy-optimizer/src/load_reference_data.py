import sqlite3

conn = sqlite3.connect('energy_optimizer.db')
cur = conn.cursor()

# ------------------------------------------------------------
# Appliance reference data: typical/average running wattage.
# Sourced from ENERGY STAR product guidance and industry
# wattage references. These are starting points; swap in exact
# figures from the ENERGY STAR Product Finder for final submission.
# ------------------------------------------------------------

appliances = [
    # (appliance_name, default_wattage, energy_star_rated)
    ("Refrigerator",        150,  1),
    ("Window Air Conditioner", 900,  1),
    ("Washing Machine",      500,  1),
    ("Clothes Dryer",       3000,  1),
    ("Dishwasher",          1200,  1),
    ("Microwave",           1000,  0),
    ("Space Heater",        1500,  0),
    ("Television (LED)",     100,  1),
    ("Laptop",                50,  1),
    ("LED Light Bulb",         10,  1),
]

cur.executemany(
    """INSERT OR IGNORE INTO appliances (appliance_name, default_wattage, energy_star_rated)
       VALUES (?, ?, ?)""",
    appliances
)

# ------------------------------------------------------------
# Benchmark reference data: approximate average monthly kWh by
# housing type, derived from EIA RECS findings (national avg is
# ~899 kWh/month; apartments run significantly lower than
# single-family detached homes, per EIA RECS 2020).
# ------------------------------------------------------------

benchmarks = [
    # (housing_type, region, benchmark_kwh_monthly)
    ("Studio",       None, 250),
    ("Apartment",    None, 350),
    ("Condo",        None, 450),
    ("Multi-family", None, 400),
    ("Other",        None, 600),
]

cur.executemany(
    """INSERT OR IGNORE INTO benchmarks (housing_type, region, benchmark_kwh_monthly)
       VALUES (?, ?, ?)""",
    benchmarks
)

conn.commit()

# Confirm what got loaded
print("Appliances loaded:")
for row in cur.execute("SELECT appliance_name, default_wattage FROM appliances"):
    print(" ", row)

print("\nBenchmarks loaded:")
for row in cur.execute("SELECT housing_type, benchmark_kwh_monthly FROM benchmarks"):
    print(" ", row)

conn.close()
