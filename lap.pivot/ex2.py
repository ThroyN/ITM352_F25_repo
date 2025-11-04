import pandas as pd
import numpy as np
import warnings

URL = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    try:
        df = pd.read_csv(
            URL,
            dtype_backend="pyarrow",
            on_bad_lines="skip",
            low_memory=False
        )
        source = "URL"
    except Exception as e:
        print(f"[Info] Could not read from URL: {e}")
        print("[Info] Attempting to read local file sales_data.csv instead...")
        df = pd.read_csv(
            "sales_data.csv",
            dtype_backend="pyarrow",
            on_bad_lines="skip",
            low_memory=False
        )
        source = "local file"

print(f"\nLoaded data from: {source}\n")
print(df.head())
print("\nData Types Before Conversion:")
print(df.dtypes)

df["order_date"] = pd.to_datetime(df.get("order_date"), errors="coerce", infer_datetime_format=True)

print("\nData Types After Conversion:")
print(df.dtypes)

if caught:
    print("\nWarnings captured while reading the file:")
    for w in caught:
        print(f"- {w.category.__name__}: {w.message}")

df["quantity"] = pd.to_numeric(df.get("quantity"), errors="coerce")
df["unit_price"] = pd.to_numeric(df.get("unit_price"), errors="coerce")

df["sales"] = df["quantity"] * df["unit_price"]

df = df.dropna(subset=["sales"])

pivot = pd.pivot_table(
    df,
    index="region",
    columns="order_type",
    values="sales",
    aggfunc=np.sum,
    margins=True,
    margins_name="Total",
    fill_value=0
)

pd.set_option("display.max_columns", None)

print("\n--- Sales by Region x Order Type (with Totals) ---")
print(pivot)
