```python
#!/usr/bin/env python3
"""
Assignment 2 — Sales Data Dashboard (No Storage, Wizard R4, No Date-Range Prompt)
- Loads CSV from Google Drive or local path (R1)
- Sanitizes data, auto-maps column aliases, validates required columns
- Predefined analytics (R3) + Wizard-style custom pivot builder (R4)
- After each result, offers a one-off export (Excel preferred, CSV fallback)
"""

from __future__ import annotations
import sys, time, os, re
from typing import Dict, List, Tuple, Optional
import pandas as pd

# ============================================================
# Canonical columns & Aliases
# ============================================================
REQUIRED: Tuple[str, ...] = (
    "order_date",
    "sales_region",
    "order_type",
    "state",
    "customer_type",
    "product",
    "product_category",
    "employee_name",
    "quantity",
    "sale_price",
)

ALIASES: Dict[str, str] = {
    "customer_state": "state",
    "state": "state",

    "product": "product",
    "produce_name": "product",
    "product_name": "product",

    "sale_price": "sale_price",
    "unit_price": "sale_price",
    "price": "sale_price",

    "qty": "quantity",
    "quantity": "quantity",
}

DEFAULT_GDRIVE_VIEW_URL = "https://drive.google.com/file/d/1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA/view?usp=drive_link"

# ============================================================
# Utilities
# ============================================================
def to_uc(url_or_path: str) -> str:
    if "drive.google.com/file/d/" in url_or_path:
        try:
            fid = url_or_path.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?id={fid}&export=download"
        except Exception:
            pass
    return url_or_path

def fillna_loaded(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_numeric_dtype(out[c]):
            out[c] = out[c].fillna(0)
        else:
            out[c] = out[c].fillna("")
    return out

def ensure_datetime(df: pd.DataFrame, col: str = "order_date") -> pd.DataFrame:
    if col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
    return df

def auto_map_columns(df: pd.DataFrame) -> pd.DataFrame:
    renames: Dict[str, str] = {}
    for col in df.columns:
        key = col.strip()
        if key in ALIASES:
            target = ALIASES[key]
            if target not in df.columns:
                renames[col] = target
    if renames:
        print("Info: Auto-mapped columns →", ", ".join(f"{k}→{v}" for k,v in renames.items()))
        df = df.rename(columns=renames)
    return df

def validate_required(df: pd.DataFrame) -> List[str]:
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        print("WARNING: Missing required fields:", ", ".join(missing))
        print("         Some analytics may not work.")
    else:
        print("All required fields are present.")
    return missing

def clean_sheet_name(name: str) -> str:
    return re.sub(r'[\\/*?:\[\]]', '_', name)[:31] or "Sheet1"

def prompt_yes_no(msg: str, default: bool=False) -> bool:
    yn = "[Y/n]" if default else "[y/N]"
    while True:
        ans = input(f"{msg} {yn} ").strip().lower()
        if ans == "" and default: return True
        if ans == "" and not default: return False
        if ans in ("y","yes"): return True
        if ans in ("n","no"): return False
        print("Please answer y or n.")

def prompt_filename(default_name: str) -> str:
    ans = input(f"Enter filename (default: {default_name}): ").strip()
    return ans or default_name

def try_export_df(df: pd.DataFrame, default_basename: str) -> None:
    if not prompt_yes_no("Export this result to a file?", default=False):
        return
    suggested = f"{default_basename}.xlsx"
    fname = prompt_filename(suggested)
    root, ext = os.path.splitext(fname)
    ext = ext.lower()
    if ext not in (".xlsx", ".csv"):
        fname, ext = root + ".xlsx", ".xlsx"
    try:
        if ext == ".xlsx":
            try:
                with pd.ExcelWriter(fname) as xw:
                    df.to_excel(xw, index=True, sheet_name=clean_sheet_name(default_basename))
                print(f"Saved Excel: {fname}")
            except Exception as e:
                print(f"Excel export failed ({e}). Falling back to CSV…")
                csv_name = root + ".csv"
                df.to_csv(csv_name)
                print(f"Saved CSV: {csv_name}")
        else:
            df.to_csv(fname)
            print(f"Saved CSV: {fname}")
    except Exception as e:
        print(f"ERROR: Could not export file. Details: {e}")

# ============================================================
# Data Loading (R1)
# ============================================================
def load_data(src_arg: Optional[str]) -> pd.DataFrame:
    src = src_arg if src_arg else DEFAULT_GDRIVE_VIEW_URL
    src = to_uc(src)

    print("\n--- Sales Data Loader (R1) ---")
    print(f"Source: {src}")
    print("Status: Loading...", end="", flush=True)

    t0 = time.perf_counter()
    try:
        df = pd.read_csv(src)
    except Exception as e:
        print("\nERROR: Failed to load the CSV file.")
        print(f"Details: {e}")
        sys.exit(1)
    elapsed = time.perf_counter() - t0
    print("\rStatus: Loaded successfully.           ")

    if df.empty:
        print("ERROR: The file loaded but is empty. Exiting.")
        sys.exit(1)

    df.columns = [c.strip() for c in df.columns]
    df = auto_map_columns(df)
    df = ensure_datetime(df, "order_date")
    df = fillna_loaded(df)

    print(f"Time to load: {elapsed:.3f} seconds")
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    print("Available columns:")
    print(" - " + "\n - ".join(df.columns))
    validate_required(df)
    print("\nR1 complete. Data is loaded and sanitized for downstream analytics.")
    return df

# ============================================================
# Helpers for analytics
# ============================================================
def check_cols(df: pd.DataFrame, needed: set):
    missing = needed - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {', '.join(sorted(missing))}")

def build_total_column(df: pd.DataFrame) -> pd.DataFrame:
    check_cols(df, {"quantity","sale_price"})
    return df.assign(total=df["quantity"] * df["sale_price"])

# ============================================================
# Analytics (R3)
# ============================================================
def analytic_1_head(df: pd.DataFrame, label: str) -> pd.DataFrame:
    try:
        n = int(input("Show how many rows? (default 10): ").strip() or "10")
    except Exception:
        n = 10
    res = df.head(n)
    print(f"\n=== First {n} rows {label} ===")
    print(res)
    try_export_df(res, f"first_{n}_rows_{label.strip('[]').replace('..','_')}")
    return res

def analytic_2_total_sales_by_region_type(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"sales_region","order_type","quantity","sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = pd.pivot_table(
        tmp, index="sales_region", columns="order_type", values="total", aggfunc="sum"
    ).round(2)
    print(f"\n=== Total sales by region & order_type {label} ===")
    print(res)
    try_export_df(res, f"total_sales_region_ordertype_{label.strip('[]').replace('..','_')}")
    return res

def analytic_3_avg_sales_region_state_type(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"sales_region","state","order_type","sale_price"}
    check_cols(df, needed)
    res = pd.pivot_table(
        df, index="sales_region", columns=["state","order_type"], values="sale_price", aggfunc="mean"
    ).round(2)
    print(f"\n=== Average sales by region/state/type {label} ===")
    print(res)
    try_export_df(res, f"avg_sales_region_state_type_{label.strip('[]').replace('..','_')}")
    return res

def analytic_4_sales_by_custtype_ordertype_state(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"state","customer_type","order_type","quantity","sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = pd.pivot_table(
        tmp, index="state", columns=["customer_type","order_type"], values="total", aggfunc="sum"
    ).round(2)
    print(f"\n=== Sales by customer type & order type by state {label} ===")
    print(res)
    try_export_df(res, f"sales_by_custtype_ordertype_state_{label.strip('[]').replace('..','_')}")
    return res

def analytic_5_qty_and_sales_by_region_product(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"sales_region","product","quantity","sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = pd.pivot_table(
        tmp, index=["sales_region","product"], values=["quantity","total"], aggfunc="sum"
    ).sort_index()
    if ("quantity","sum") in res.columns:
        res[("quantity","sum")] = pd.to_numeric(res[("quantity","sum")], errors="coerce")
    if ("total","sum") in res.columns:
        res[("total","sum")] = pd.to_numeric(res[("total","sum")], errors="coerce").round(2)
    print(f"\n=== Total quantity & total sales by region/product {label} ===")
    print(res.head(30))
    try_export_df(res, f"qty_sales_by_region_product_{label.strip('[]').replace('..','_')}")
    return res

def analytic_6_qty_and_sales_by_customer_type(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"customer_type","quantity","sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = pd.pivot_table(
        tmp, index="customer_type", values=["quantity","total"], aggfunc="sum"
    )
    if ("quantity","sum") in res.columns:
        res[("quantity","sum")] = pd.to_numeric(res[("quantity","sum")], errors="coerce")
    if ("total","sum") in res.columns:
        res[("total","sum")] = pd.to_numeric(res[("total","sum")], errors="coerce").round(2)
    print(f"\n=== Total quantity & total sales by customer type {label} ===")
    print(res)
    try_export_df(res, f"qty_sales_by_customer_type_{label.strip('[]').replace('..','_')}")
    return res

def analytic_7_max_min_unit_price_by_category(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"product_category","sale_price"}
    check_cols(df, needed)
    res = pd.pivot_table(
        df, index="product_category", values="sale_price", aggfunc=["max","min"]
    ).round(2)
    print(f"\n=== Max & min unit price by category {label} ===")
    print(res)
    try_export_df(res, f"max_min_unit_price_by_category_{label.strip('[]').replace('..','_')}")
    return res

def analytic_8_unique_employees_by_region(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"sales_region","employee_name"}
    check_cols(df, needed)
    res = pd.pivot_table(
        df, index="sales_region", values="employee_name", aggfunc=pd.Series.nunique
    ).rename(columns={"employee_name":"unique_employees"})
    print(f"\n=== Number of unique employees by region {label} ===")
    print(res)
    try_export_df(res, f"unique_employees_by_region_{label.strip('[]').replace('..','_')}")
    return res

# ============================================================
# Wizard-Style Custom Pivot (R4)
# ============================================================
def create_custom_pivot_r4(df: pd.DataFrame) -> pd.DataFrame:
    scoped = df.copy()
    label = "[all]"

    # Map aliases and add total_sales if possible
    rename_map = {c: ALIASES.get(c, c) for c in scoped.columns}
    if any(rename_map[c] != c for c in scoped.columns):
        scoped = scoped.rename(columns=rename_map)
    if {"quantity", "sale_price"}.issubset(scoped.columns) and "total_sales" not in scoped.columns:
        scoped["total_sales"] = pd.to_numeric(scoped["quantity"], errors="coerce").fillna(0) * \
                                pd.to_numeric(scoped["sale_price"], errors="coerce").fillna(0)

    # Build numbered field list (show only those that exist)
    candidates = [
        "order_number","employee_id","employee_name","job_title","sales_region",
        "order_date","order_type","customer_type","customer_name","state",
        "product_category","product_number","product","quantity","sale_price","total_sales"
    ]
    fields = [c for c in candidates if c in scoped.columns]

    print("\n============================================================")
    print("CREATE CUSTOM PIVOT TABLE (R4)")
    print("============================================================\n")
    print("============================================================")
    print("CUSTOM PIVOT TABLE GENERATOR")
    print("============================================================\n")
    print("This tool allows you to create custom pivot tables from your data.\n")

    def show_choices(title: str):
        print("------------------------------------------------------------")
        print(title)
        print("------------------------------------------------------------")
        for i, c in enumerate(fields, start=1):
            print(f"{i}. {c}")

    def parse_multi(prompt: str) -> list[str]:
        raw = input(prompt).strip()
        if not raw:
            return []
        idxs = []
        for piece in raw.split(","):
            s = piece.strip()
            if not s:
                continue
            if not s.isdigit():
                continue
            i = int(s)
            if 1 <= i <= len(fields):
                idxs.append(i-1)
        # dedupe preserve order
        seen, out = set(), []
        for i in idxs:
            if i not in seen:
                out.append(i); seen.add(i)
        return [fields[i] for i in out]

    # STEP 1: rows
    show_choices("STEP 1: Select Row Dimensions")
    rows = parse_multi("Enter the number(s) of your choice(s), separated by commas: ")

    # STEP 2: columns
    show_choices("\nSTEP 2: Select Column Dimensions")
    cols = parse_multi("Enter the number(s) of your choice(s), separated by commas: ")

    # STEP 3: value
    print("\n------------------------------------------------------------")
    print("STEP 3: Select Value (single)")
    print("------------------------------------------------------------")
    for i, c in enumerate(fields, start=1):
        print(f"{i}. {c}")
    val_idx_raw = input("Enter ONE number for the Value field: ").strip()
    try:
        val_idx = int(val_idx_raw)
        if not (1 <= val_idx <= len(fields)):
            raise ValueError
        value_field = fields[val_idx-1]
    except Exception:
        raise KeyError("Invalid value selection.")

    # STEP 4: aggregation
    print("\n------------------------------------------------------------")
    print("STEP 4: Aggregation")
    print("------------------------------------------------------------")
    agg = input("Aggregation (sum/mean/count/max/min; default=sum): ").strip().lower() or "sum"
    aggfunc_map = {"sum":"sum","mean":"mean","avg":"mean","count":"count","max":"max","min":"min"}
    aggfunc = aggfunc_map.get(agg, "sum")

    # Build pivot
    pivot = pd.pivot_table(
        scoped,
        index=rows or None,
        columns=cols or None,
        values=value_field,
        aggfunc=aggfunc
    )
    try:
        if pd.api.types.is_numeric_dtype(pivot):
            pivot = pivot.round(2)
    except Exception:
        pass

    print(f"\n=== Custom Pivot ({aggfunc} of {value_field}) {label} ===")
    print(pivot.head(30))
    safe_name = f"custom_pivot_{aggfunc}_of_{value_field}_{label.strip('[]').replace('..','_')}"
    try_export_df(pivot, safe_name)
    return pivot

# ============================================================
# Menu / UI (R2)
# ============================================================
def print_menu():
    print("============================================================")
    print("SALES DATA DASHBOARD")
    print("============================================================")
    print("1. Show the first n rows")
    print("2. Total sales by region & order_type")
    print("3. Average sales by region/state/type")
    print("4. Sales by customer type & order type by state")
    print("5. Total quantity & total sales by region/product")
    print("6. Total quantity & total sales by customer type")
    print("7. Max & min unit price by category")
    print("8. Number of unique employees by region")
    print("9. Create custom pivot table (R4)")
    print("10. Exit")
    print("============================================================")
    print()

def main() -> None:
    src_arg = sys.argv[1] if len(sys.argv) > 1 else None
    df = load_data(src_arg)
    label = "[all]"

    while True:
        print_menu()
        choice = input("Enter choice (1-10 or 'q' to quit): ").strip().lower()

        if choice in ("q","10"):
            print("Goodbye.")
            break

        try:
            if choice == "1":
                analytic_1_head(df, label)
            elif choice == "2":
                analytic_2_total_sales_by_region_type(df, label)
            elif choice == "3":
                analytic_3_avg_sales_region_state_type(df, label)
            elif choice == "4":
                analytic_4_sales_by_custtype_ordertype_state(df, label)
            elif choice == "5":
                analytic_5_qty_and_sales_by_region_product(df, label)
            elif choice == "6":
                analytic_6_qty_and_sales_by_customer_type(df, label)
            elif choice == "7":
                analytic_7_max_min_unit_price_by_category(df, label)
            elif choice == "8":
                analytic_8_unique_employees_by_region(df, label)
            elif choice == "9":
                create_custom_pivot_r4(df)
            else:
                print("Unknown choice. Try again.")
        except KeyError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

