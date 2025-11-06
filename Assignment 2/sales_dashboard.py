#!/usr/bin/env python3
"""
Assignment 2 — Sales Data Dashboard (With In-App Storage & Stored Results Menu)
- Loads CSV from Google Drive or local path (R1)
- Sanitizes data, auto-maps column aliases, validates required columns
- Predefined analytics (R3) + Wizard-style custom pivot builder (R4)
- After each result, offers a one-off export (Excel preferred, CSV fallback)
- NEW: Keeps track of all analytics produced in-session, lists them above the menu,
       and adds a menu option to browse/export stored results (R2+R4 enhancement)
"""

from __future__ import annotations

import os
import re
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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
# In-memory Store (NEW)
# ============================================================
STORE: Dict[str, pd.DataFrame] = {}
STORE_META: Dict[str, str] = {}


def _now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _unique_key(base: str) -> str:
    base = base.strip().replace("  ", " ")
    if base not in STORE:
        return base
    i = 2
    while f"{base} ({i})" in STORE:
        i += 1
    return f"{base} ({i})"


def add_to_store(df: pd.DataFrame, base_name: str, detail: str) -> str:
    key = _unique_key(base_name)
    STORE[key] = df
    shape = f"{df.shape[0]}x{df.shape[1]}"
    STORE_META[key] = f"{detail} | {shape} | saved { _now_stamp() }"
    return key


def print_store_summary_inline(max_items: int = 6) -> None:
    print("------------------------------------------------------------")
    print("Stored results (this session):", len(STORE))
    if not STORE:
        print(" - (none yet)")
    else:
        for i, (name, meta) in enumerate(STORE_META.items()):
            if i >= max_items:
                print(f" - ...and {len(STORE)-max_items} more (use option 10)")
                break
            print(f" - {name}  [{STORE[name].shape[0]}x{STORE[name].shape[1]}]")
    print("------------------------------------------------------------")


def browse_stored_results() -> None:
    if not STORE:
        print("\nNo stored results yet.")
        return

    print("\n================ STORED RESULTS ================")
    names = list(STORE.keys())
    for i, name in enumerate(names, start=1):
        meta = STORE_META.get(name, "")
        print(f"{i}. {name}")
        if meta:
            print(f"   {meta}")
    print("================================================")

    sel = input(
        "\nEnter number to view/export, 'a' to export all to separate files, or press Enter to go back: "
    ).strip().lower()
    if sel == "":
        return
    if sel == "a":
        for name in names:
            df = STORE[name]
            safe_base = re.sub(r"[^a-zA-Z0-9_\-]+", "_", name)[:60] or "stored_result"
            try_export_df(df, safe_base)
        return
    if not sel.isdigit():
        print("Invalid selection.")
        return
    idx = int(sel)
    if not (1 <= idx <= len(names)):
        print("Invalid selection.")
        return

    name = names[idx - 1]
    df = STORE[name]
    print(f"\n=== {name} ===")
    print(df.head(30))
    try_export_df(df, re.sub(r"[^a-zA-Z0-9_\-]+", "_", name)[:60] or "stored_result")


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
        print("Info: Auto-mapped columns →", ", ".join(f"{k}→{v}" for k, v in renames.items()))
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
    return re.sub(r"[\\/*?:\[\]]", "_", name)[:31] or "Sheet1"


def prompt_yes_no(msg: str, default: bool = False) -> bool:
    yn = "[Y/n]" if default else "[y/N]"
    while True:
        ans = input(f"{msg} {yn} ").strip().lower()
        if ans == "" and default:
            return True
        if ans == "" and not default:
            return False
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
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


# ---------- Wizard helpers (input robustness & numeric safety) ----------
NUMERIC_AGGS = {"sum", "mean", "avg", "max", "min"}


def pick_from_numbered_list(items: List[str], prompt: str) -> str:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(items):
                return items[i - 1]
        print(f"Please enter a number between 1 and {len(items)}.")


def normalize_agg(raw: str) -> str:
    m = (raw or "sum").strip().lower()
    return {"avg": "mean"}.get(m, m)


def ensure_value_and_agg_compatible(df: pd.DataFrame, value_field: str, aggfunc: str) -> tuple[str, str]:
    if value_field not in df.columns:
        return value_field, aggfunc
    series = df[value_field]
    is_num = pd.api.types.is_numeric_dtype(series)

    if aggfunc in NUMERIC_AGGS and not is_num:
        coerced = pd.to_numeric(series, errors="coerce")
        if coerced.notna().any():
            tmp_name = f"__num__{value_field}"
            df[tmp_name] = coerced.fillna(0)
            print(f"Info: Coerced '{value_field}' to numeric for '{aggfunc}'.")
            return tmp_name, aggfunc
        else:
            print(f"Note: '{value_field}' is non-numeric; switching aggregation to 'count'.")
            return value_field, "count"
    return value_field, aggfunc


# ---------- FIXED: Dynamic-menu helpers ----------
def _render_choices(fields: List[str], exclude: set[str]) -> List[str]:
    """Return a list excluding any in `exclude`, preserving order."""
    return [f for f in fields if f not in exclude]


def _pick_multi_from(fields: List[str], prompt: str) -> List[str]:
    """Show a numbered list and return selected fields (deduped, ordered). Empty allowed."""
    if not fields:
        print("(no available fields)")
        return []

    for i, c in enumerate(fields, start=1):
        print(f"{i}. {c}")

    while True:
        raw = input(prompt).strip()
        if raw == "":
            return []
        ok = True
        idxs: List[int] = []
        for piece in raw.split(","):
            s = piece.strip()
            if not s.isdigit():
                ok = False
                break
            i = int(s)
            if not (1 <= i <= len(fields)):
                ok = False
                break
            idxs.append(i - 1)
        if ok:
            seen, out = set(), []
            for i in idxs:
                if i not in seen:
                    out.append(fields[i])
                    seen.add(i)
            return out
        print(f"Please enter comma-separated numbers between 1 and {len(fields)} (or press Enter to skip).")


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
    check_cols(df, {"quantity", "sale_price"})
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
    needed = {"sales_region", "order_type", "quantity", "sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = (
        pd.pivot_table(tmp, index="sales_region", columns="order_type", values="total", aggfunc="sum")
        .round(2)
    )
    print(f"\n=== Total sales by region & order_type {label} ===")
    print(res)
    try_export_df(res, f"total_sales_region_ordertype_{label.strip('[]').replace('..','_')}")
    return res


def analytic_3_avg_sales_region_state_type(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"sales_region", "state", "order_type", "sale_price"}
    check_cols(df, needed)
    res = (
        pd.pivot_table(
            df, index="sales_region", columns=["state", "order_type"], values="sale_price", aggfunc="mean"
        ).round(2)
    )
    print(f"\n=== Average sales by region/state/type {label} ===")
    print(res)
    try_export_df(res, f"avg_sales_region_state_type_{label.strip('[]').replace('..','_')}")
    return res


def analytic_4_sales_by_custtype_ordertype_state(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"state", "customer_type", "order_type", "quantity", "sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = (
        pd.pivot_table(
            tmp, index="state", columns=["customer_type", "order_type"], values="total", aggfunc="sum"
        ).round(2)
    )
    print(f"\n=== Sales by customer type & order type by state {label} ===")
    print(res)
    try_export_df(res, f"sales_by_custtype_ordertype_state_{label.strip('[]').replace('..','_')}")
    return res


def analytic_5_qty_and_sales_by_region_product(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"sales_region", "product", "quantity", "sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = pd.pivot_table(tmp, index=["sales_region", "product"], values=["quantity", "total"], aggfunc="sum").sort_index()
    if ("quantity", "sum") in res.columns:
        res[("quantity", "sum")] = pd.to_numeric(res[("quantity", "sum")], errors="coerce")
    if ("total", "sum") in res.columns:
        res[("total", "sum")] = pd.to_numeric(res[("total", "sum")], errors="coerce").round(2)
    print(f"\n=== Total quantity & total sales by region/product {label} ===")
    print(res.head(30))
    try_export_df(res, f"qty_sales_by_region_product_{label.strip('[]').replace('..','_')}")
    return res


def analytic_6_qty_and_sales_by_customer_type(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"customer_type", "quantity", "sale_price"}
    check_cols(df, needed)
    tmp = build_total_column(df)
    res = pd.pivot_table(tmp, index="customer_type", values=["quantity", "total"], aggfunc="sum")
    if ("quantity", "sum") in res.columns:
        res[("quantity", "sum")] = pd.to_numeric(res[("quantity", "sum")], errors="coerce")
    if ("total", "sum") in res.columns:
        res[("total", "sum")] = pd.to_numeric(res[("total", "sum")], errors="coerce").round(2)
    print(f"\n=== Total quantity & total sales by customer type {label} ===")
    print(res)
    try_export_df(res, f"qty_sales_by_customer_type_{label.strip('[]').replace('..','_')}")
    return res


def analytic_7_max_min_unit_price_by_category(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"product_category", "sale_price"}
    check_cols(df, needed)
    res = pd.pivot_table(df, index="product_category", values="sale_price", aggfunc=["max", "min"]).round(2)
    print(f"\n=== Max & min unit price by category {label} ===")
    print(res)
    try_export_df(res, f"max_min_unit_price_by_category_{label.strip('[]').replace('..','_')}")
    return res


def analytic_8_unique_employees_by_region(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"sales_region", "employee_name"}
    check_cols(df, needed)
    res = pd.pivot_table(df, index="sales_region", values="employee_name", aggfunc=pd.Series.nunique).rename(
        columns={"employee_name": "unique_employees"}
    )
    print(f"\n=== Number of unique employees by region {label} ===")
    print(res)
    try_export_df(res, f"unique_employees_by_region_{label.strip('[]').replace('..','_')}")
    return res


# ============================================================
# Wizard-Style Custom Pivot (R4) — FIXED DYNAMIC MENUS
# ============================================================
def create_custom_pivot_r4(df: pd.DataFrame) -> pd.DataFrame:
    scoped = df.copy()
    label = "[all]"

    # Map aliases and add total_sales if possible
    rename_map = {c: ALIASES.get(c, c) for c in scoped.columns}
    if any(rename_map[c] != c for c in scoped.columns):
        scoped = scoped.rename(columns=rename_map)
    if {"quantity", "sale_price"}.issubset(scoped.columns) and "total_sales" not in scoped.columns:
        scoped["total_sales"] = pd.to_numeric(scoped["quantity"], errors="coerce").fillna(0) * pd.to_numeric(
            scoped["sale_price"], errors="coerce"
        ).fillna(0)

    # Build base field list (only existing)
    candidates = [
        "order_number",
        "employee_id",
        "employee_name",
        "job_title",
        "sales_region",
        "order_date",
        "order_type",
        "customer_type",
        "customer_name",
        "state",
        "product_category",
        "product_number",
        "product",
        "quantity",
        "sale_price",
        "total_sales",
    ]
    base_fields = [c for c in candidates if c in scoped.columns]

    print("\n============================================================")
    print("CREATE CUSTOM PIVOT TABLE (R4)")
    print("============================================================\n")
    print("CUSTOM PIVOT TABLE GENERATOR (dynamic menus)\n")

    # STEP 1: Rows (full list, nothing excluded yet)
    print("------------------------------------------------------------")
    print("STEP 1: Select Row Dimensions")
    print("------------------------------------------------------------")
    rows_menu = _render_choices(base_fields, exclude=set())
    rows = _pick_multi_from(rows_menu, "Enter the number(s) of your choice(s), separated by commas: ")
    print(f"Rows set to: {rows if rows else ['(none)']}")

    # STEP 2: Columns (exclude rows that were just selected)
    print("\n------------------------------------------------------------")
    print("STEP 2: Select Column Dimensions")
    print("------------------------------------------------------------")
    cols_menu = _render_choices(base_fields, exclude=set(rows))
    cols = _pick_multi_from(cols_menu, "Enter the number(s) of your choice(s), separated by commas: ")
    print(f"Columns set to: {cols if cols else ['(none)']}")

    # STEP 3: Value (exclude both rows and columns)
    print("\n------------------------------------------------------------")
    print("STEP 3: Select Value (single)")
    print("------------------------------------------------------------")
    exclude = set(rows) | set(cols)
    value_menu = _render_choices(base_fields, exclude=exclude)

    if not value_menu:
        print("Note: all fields were used in rows/columns; allowing value selection from all fields.")
        value_menu = base_fields[:]

    for i, c in enumerate(value_menu, start=1):
        print(f"{i}. {c}")

    value_field = pick_from_numbered_list(value_menu, "Enter ONE number for the Value field: ")
    print(f"Value set to: {value_field}")

    # STEP 4: aggregation (normalize + compatibility)
    print("\n------------------------------------------------------------")
    print("STEP 4: Aggregation")
    print("------------------------------------------------------------")
    print("Choose how the values should be summarized:")
    print(" - sum   = total")
    print(" - mean  = average")
    print(" - count = how many")
    print(" - max   = highest value")
    print(" - min   = lowest value")
    agg = normalize_agg(input("Type one (sum/mean/count/max/min) or press Enter for sum: "))
    value_field_use, agg_use = ensure_value_and_agg_compatible(scoped, value_field, agg)
    if (agg_use != agg) or (value_field_use != value_field):
        print(f"Using aggregation '{agg_use}' on field '{value_field_use}'.")

    # Build pivot
    print("\nBuilding pivot…")
    pivot = pd.pivot_table(
        scoped,
        index=rows or None,
        columns=cols or None,
        values=value_field_use,
        aggfunc=agg_use,
    )
    try:
        if pd.api.types.is_numeric_dtype(pivot):
            pivot = pivot.round(2)
    except Exception:
        pass

    print(f"\n=== Custom Pivot ({agg_use} of {value_field}) {label} ===")
    print(pivot.head(30))
    safe_name = f"custom_pivot_{agg_use}_of_{value_field}_{label.strip('[]').replace('..','_')}"
    try_export_df(pivot, safe_name)

    # Store & optional rename
    default_entry = f"R4: {agg_use}({value_field}) rows={rows or ['∅']} cols={cols or ['∅']}"
    final_key = add_to_store(pivot, default_entry, "Custom pivot (wizard)")
    if prompt_yes_no("Rename this stored result entry?", default=False):
        new_name = input("Enter a new name for this stored result: ").strip()
        if new_name:
            df_copy = STORE.pop(final_key)
            meta = STORE_META.pop(final_key)
            final_key = _unique_key(new_name)
            STORE[final_key] = df_copy
            STORE_META[final_key] = meta
    print(f"Stored as: {final_key}")
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
    print("10. View/export stored results (NEW)")
    print("11. Exit")
    print("============================================================")
    print()


def main() -> None:
    src_arg = sys.argv[1] if len(sys.argv) > 1 else None
    df = load_data(src_arg)
    label = "[all]"

    while True:
        print_store_summary_inline()
        print_menu()
        choice = input("Enter choice (1-11 or 'q' to quit): ").strip().lower()

        if choice in ("q", "11"):
            print("Goodbye.")
            break

        try:
            if choice == "1":
                res = analytic_1_head(df, label)
                add_to_store(res, "R3.1: head()", "First n rows")
            elif choice == "2":
                res = analytic_2_total_sales_by_region_type(df, label)
                add_to_store(res, "R3.2: total_sales by region x order_type", "Pivot: sum(total)")
            elif choice == "3":
                res = analytic_3_avg_sales_region_state_type(df, label)
                add_to_store(res, "R3.3: avg sale_price by region x state x order_type", "Pivot: mean(sale_price)")
            elif choice == "4":
                res = analytic_4_sales_by_custtype_ordertype_state(df, label)
                add_to_store(res, "R3.4: sales by cust_type x order_type x state", "Pivot: sum(total)")
            elif choice == "5":
                res = analytic_5_qty_and_sales_by_region_product(df, label)
                add_to_store(res, "R3.5: qty & sales by region x product", "Pivot: sum(quantity,total)")
            elif choice == "6":
                res = analytic_6_qty_and_sales_by_customer_type(df, label)
                add_to_store(res, "R3.6: qty & sales by customer_type", "Pivot: sum(quantity,total)")
            elif choice == "7":
                res = analytic_7_max_min_unit_price_by_category(df, label)
                add_to_store(res, "R3.7: max/min unit price by category", "Pivot: max/min(sale_price)")
            elif choice == "8":
                res = analytic_8_unique_employees_by_region(df, label)
                add_to_store(res, "R3.8: unique employees by region", "Pivot: nunique(employee_name)")
            elif choice == "9":
                create_custom_pivot_r4(df)
            elif choice == "10":
                browse_stored_results()
            else:
                print("Unknown choice. Try again.")
        except KeyError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
