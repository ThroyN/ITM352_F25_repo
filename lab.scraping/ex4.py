from sodapy import Socrata
import pandas as pd

# ---- Connect to Chicago's Socrata portal (no app token needed for small pulls) ----
client = Socrata("data.cityofchicago.org", None)

# ---- Pull first 500 records from passenger vehicle licenses dataset (rr23-ymwb) ----
results = client.get("rr23-ymwb", limit=500)

# ---- Convert to DataFrame ----
df = pd.DataFrame.from_records(results)

# Quick sanity check: what columns did we get?
print("Columns:", list(df.columns))
print("\nHead:\n", df.head())

# ---- Find likely vehicle and fuel columns, even if names vary ----
lower_cols = {c.lower(): c for c in df.columns}
# Try common possibilities
vehicle_candidates = [c for c in df.columns if "vehicle" in c.lower() and "license" not in c.lower()]
fuel_candidates    = [c for c in df.columns if "fuel" in c.lower()]

vehicle_col = vehicle_candidates[0] if vehicle_candidates else lower_cols.get("vehicle", None)
fuel_col    = fuel_candidates[0] if fuel_candidates else (lower_cols.get("fuel_source") or lower_cols.get("fuel_type"))

if not vehicle_col or not fuel_col:
    raise RuntimeError(
        f"Couldn’t auto-detect columns. Please check available columns above and set "
        f"`vehicle_col` and `fuel_col` manually."
    )

print(f"\nUsing columns → vehicle: '{vehicle_col}', fuel: '{fuel_col}'\n")

# ---- Print sample of vehicles and fuel sources ----
print("Sample vehicles & fuel:")
print(df[[vehicle_col, fuel_col]].head(20).to_string(index=False))

# ---- Group by fuel and count ----
fuel_counts = (
    df[fuel_col]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
    .replace({"": "Unknown"})
    .value_counts()
    .rename_axis("fuel_source")
    .reset_index(name="num_vehicles")
)

print("\nVehicles per fuel source:")
print(fuel_counts.to_string(index=False))
