"""
Assignment 2 — Sales Data Dashboard

This program is a text-based dashboardfor exp loring sales data with Pandas.
It loads the CSV from Google Drive or a local path (R1), cleans up column names
(using simple alias mapping), checks the required fields, and converts dates.

Features:
- R1: Load and sanitize data (strip/alias columns, coerce order_date to datetime).
- R2: Menu-driven UI so it can run different analyses in one session.
- R3: A set of predefined pivots (totals, averages, counts) for common questions.
- R4: A wizard to build custom pivot tables by choosing rows, columns, value, and aggregation.

Personal add-ons:
- After each result, the app offers to export to Excel (falls back to CSV if needed).
- The app keeps an in-memory list of everything I ran this session and lets me view
  or export those results later from a separate menu option.

Notes:
- The Google Drive link is converted to a direct "uc" download URL automatically.
- For Excel exports, this program uses openpyxl.
- If it's not installed, install it with: pip install openpyxl
- (If using a venv, activate it first.)

=============================================================================
AI USAGE DOCUMENTATION
=============================================================================

I used Claude (Anthropic's AI) throughout this project to help me learn pandas
better and debug problems when I got stuck. Here's everything I used it for:

1. LEARNING PANDAS SYNTAX:
   - I knew what pivot tables were from class but couldn't figure out the syntax
     for doing multi-level columns in pandas
   - My prompt: "How do I create a pivot table in pandas with multiple columns 
     as the index and specify different aggregation functions?"
   - AI gave me some example code and I changed it to work with my data
   - Functions I used this in: analytic_3_avg_sales_region_state_type, 
     analytic_5_qty_and_sales_by_region_product

2. DEBUGGING DATE CONVERSION:
   - My dates kept showing up as NaT (Not a Time) and I couldn't figure out why
   - My prompt: "Why is pd.to_datetime not working on my date column? Getting 
     NaT values"
   - AI told me to add errors='coerce' and infer_datetime_format which fixed it
   - Function: ensure_datetime()

3. INPUT VALIDATION LOGIC:
   - I wrote some basic validation but my program kept crashing on weird inputs
   - My prompt: "How do I validate comma-separated numeric input in Python and 
     handle invalid entries gracefully?"
   - AI showed me how to use isdigit() and check ranges, then I adapted it
   - Function: _pick_multi_from()

4. EXCEL EXPORT ERROR HANDLING:
   - My program crashed whenever openpyxl wasn't installed on someone's computer
   - My prompt: "How do I catch ImportError exceptions and fallback to CSV export?"
   - AI explained try-except blocks and how to handle different exceptions
   - Function: try_export_df()

5. GOOGLE DRIVE URL CONVERSION:
   - Had no idea how to make pandas read directly from a Drive link
   - My prompt: "What's the URL format to directly download a file from Google 
     Drive using its file ID?"
   - AI gave me the uc?id= format and I wrote the code to extract the file ID
   - Function: to_uc()

6. CODE ORGANIZATION:
   - Wasn't sure if I should put everything in one big function or split it up
   - My prompt: "Is it better to have one large function or break pivot table 
     creation into smaller helper functions?"
   - AI said to split things up which made sense, so I made the helper functions

Everything else is my own work - I designed all the analytics, wrote the menu
system, came up with the stored results feature, and put together the overall
structure. I mainly used AI when I got stuck on syntax or needed to learn
something new that we didn't cover in class yet.

=============================================================================
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

# List of columns that must exist in the dataset for the analytics to work.
# The program checks for these after loading the CSV.

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
# Some datasets use different names for the same column.
# This dictionary maps alternate names to the standard names used in the analysis.

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

# Returns the current date and time as a formatted string.
# Used for labeling when a result was stored.

def _now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Ensures that each stored result has a unique name.
# If the base name is already used, the function adds (2), (3), etc.
# This prevents overwriting previously stored results.

def _unique_key(base: str) -> str:
    base = base.strip().replace("  ", " ")
    if base not in STORE:
        return base
    i = 2
    while f"{base} ({i})" in STORE:
        i += 1
    return f"{base} ({i})"

# Adds a new result to the in-memory store.
# Uses _unique_key so names do not overwrite each other.
# Also records a short description and timestamp for display later.

def add_to_store(df: pd.DataFrame, base_name: str, detail: str) -> str:
    key = _unique_key(base_name)
    STORE[key] = df
    shape = f"{df.shape[0]}x{df.shape[1]}"
    STORE_META[key] = f"{detail} | {shape} | saved { _now_stamp() }"
    return key

# Prints a short list of stored results at the top of the menu.
# Shows how many results are saved and displays up to max_items.
# Helps keep track of previous analyses during the session.


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


# Allows the user to browse stored results from this session.
# Displays each saved result with its name and details, then gives options:
# - Select a result to view and optionally export it
# - Export all stored results at once
# - Or return to the main menu
# Includes input checks so the user cannot select something invalid.

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

# Converts a regular Google Drive sharing link into a direct download link.
# This lets pandas load the CSV file without manually downloading it first.
#
# AI HELP:
# - Had no clue what the direct download format was for Google Drive
# - Asked: "What's the URL format to directly download a file from Google 
#   Drive using its file ID?"
# - AI told me about the /uc?id= thing and the export=download part
# - I figured out the string parsing with split() on my own

def to_uc(url_or_path: str) -> str:
    if "drive.google.com/file/d/" in url_or_path:
        try:
            fid = url_or_path.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?id={fid}&export=download"
        except Exception:
            pass
    return url_or_path

# Fills any missing values in the dataset.
# Numeric columns get 0, and non-numeric columns get an empty string.
# This helps avoid errors later when running pivot tables.


def fillna_loaded(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_numeric_dtype(out[c]):
            out[c] = out[c].fillna(0)
        else:
            out[c] = out[c].fillna("")
    return out



# Converts the order_date column to proper datetime format if it isn't already.
# This ensures date filtering and time-based operations work correctly.
#
# AI HELP:
# - My dates kept coming out as NaT (Not a Time) and I was confused why
# - Asked: "Why is pd.to_datetime not working on my date column? Getting 
#   NaT values"
# - AI said to add errors='coerce' and told me about infer_datetime_format
# - I added the dtype check part myself using is_datetime64_any_dtype

def ensure_datetime(df: pd.DataFrame, col: str = "order_date") -> pd.DataFrame:
    if col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
    return df



# Automatically renames columns based on the ALIASES dictionary.
# This helps standardize column names when the dataset uses slightly different labels.
# If any columns are renamed, a message is printed to show what changed.


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

# Checks whether all required columns are present in the dataset.
# If any are missing, it prints a warning so the user knows some analytics may fail.

def validate_required(df: pd.DataFrame) -> List[str]:
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        print("WARNING: Missing required fields:", ", ".join(missing))
        print("         Some analytics may not work.")
    else:
        print("All required fields are present.")
    return missing

# Makes sure a provided name is valid to use as an Excel sheet name.
# Excel does not allow certain characters in sheet names, so those are replaced.
# Also limits the name length to 31 characters, which is Excel's maximum.
# If the final result is empty, it defaults to "Sheet1".

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

# Asks the user to enter a filename when exporting results.
# If the user just presses Enter, the default filename provided is used.
# Strips extra spaces from the input to avoid formatting issues.
# Helps keep file naming simple and consistent.


def prompt_filename(default_name: str) -> str:
    ans = input(f"Enter filename (default: {default_name}): ").strip()
    return ans or default_name

# Handles exporting a DataFrame to either Excel (.xlsx) or CSV.
# Asks the user if they want to export, then prompts for a filename.
# Tries to save as Excel first; if that fails or is not supported, it falls back to CSV.
# Ensures exports do not break even if the system is missing Excel-related packages.
#
# AI HELP:
# - My program kept crashing when someone didn't have openpyxl installed
# - Asked: "How do I catch ImportError exceptions and fallback to CSV export?"
# - AI explained try-except blocks and how to catch specific exceptions
# - I came up with the user flow and fallback logic myself, AI just helped
#   with the exception syntax

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

# Displays a list of selectable items and lets the user choose by typing a number.
# Checks that the user input is a valid number within the correct range.
# Continues asking until a valid selection is made.
# Returns the item that corresponds to the chosen number.

def pick_from_numbered_list(items: List[str], prompt: str) -> str:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(items):
                return items[i - 1]
        print(f"Please enter a number between 1 and {len(items)}.")

# Cleans up the user's aggregation input.
# Defaults to "sum" if nothing is entered, and converts "avg" to "mean".
# Ensures the aggregation keyword matches what Pandas expects.

def normalize_agg(raw: str) -> str:
    m = (raw or "sum").strip().lower()
    return {"avg": "mean"}.get(m, m)

# Checks whether the selected value column works with the chosen aggregation type.
# If the aggregation requires numbers but the column is not numeric, it attempts to convert it.
# If conversion works, it uses the converted version; if not, it switches to a count instead.
# This prevents errors during pivot table creation and keeps the output meaningful.

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

# Takes a list of field names and returns a new list with some removed.
# The `exclude` set contains fields that should not be shown in the selection menu.
# Keeps the original order of the remaining fields so menus stay predictable.
# Used to prevent selecting the same field twice in the pivot builder.


def _render_choices(fields: List[str], exclude: set[str]) -> List[str]:
    """Return a list excluding any in `exclude`, preserving order."""
    return [f for f in fields if f not in exclude]

# Displays a numbered menu of available fields and lets the user select multiple.
# The user can enter comma-separated numbers (e.g., "1, 3, 4") to pick multiple items.
# Ensures that only valid numbers are accepted and prevents duplicate choices.
# If the user just presses Enter, it returns an empty list, meaning "none selected."
# Maintains the order in which items were selected rather than sorting them.
# Used in the custom pivot builder for selecting rows and column dimensions.
#
# AI HELP:
# - My program crashed whenever users typed in letters or numbers that were too big
# - Asked: "How do I validate comma-separated numeric input in Python and 
#   handle invalid entries gracefully?"
# - AI showed me how to use split(), strip(), isdigit(), and check ranges
# - I took that pattern and added the deduplication stuff myself

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

# Loads the sales data from either the provided file path or the default Google Drive link.
# Converts shared Drive links to direct-download format so pandas can read them.
# Cleans up the data by trimming column names, mapping aliases, fixing dates, and filling missing values.
# Prints basic load details (row count, column list, load time) to confirm successful import.
# Returns the cleaned DataFrame so the rest of the dashboard can use it for analysis.


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

# Checks whether the required columns are present in the DataFrame.
# If any are missing, it raises an error so the analysis doesn't continue incorrectly.
# Helps prevent pivot tables from failing later on.

def check_cols(df: pd.DataFrame, needed: set):
    missing = needed - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {', '.join(sorted(missing))}")

# Adds a new column called "total" that calculates quantity * sale_price.
# First checks that both quantity and sale_price exist in the data.
# Used in several analytics that require total sales values.

def build_total_column(df: pd.DataFrame) -> pd.DataFrame:
    check_cols(df, {"quantity", "sale_price"})
    return df.assign(total=df["quantity"] * df["sale_price"])


# ============================================================
# Analytics (R3)
# ============================================================

# Displays the first few rows of the dataset so the user can preview the data.
# Lets the user choose how many rows to show, with a default of 10 if nothing is entered.
# Prints the preview and gives the option to export it to a file.
# Returns the displayed rows so they can also be stored in the session history.



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


# Calculates total sales grouped by region and order type.
# Uses quantity * sale_price to compute total sales before building the pivot table.
# The pivot table organizes regions as rows and order types as columns for easy comparison.
# Prints the result and offers the option to export it before returning the table.


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



# Computes the average sale price grouped by region, state, and order type.
# Uses a pivot table so regions are rows, and (state, order type) combinations form the columns.
# Rounds the results to two decimals to keep the output easy to read.
# Prints the table and allows the user to export the result before returning it.
#
# AI HELP:
# - I got how pivot tables work from class but couldn't figure out the syntax
#   for having multiple things as columns
# - Asked: "How do I create a pivot table in pandas with multiple columns 
#   as the index and specify different aggregation functions?"
# - AI gave me example code showing columns=["col1", "col2"] as a list
# - I used that syntax for my specific regional analysis

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

# Calculates total sales grouped by state, customer type, and order type.
# First creates a total sales value by multiplying quantity and sale price.
# Builds a pivot table to compare how different customer groups contribute to sales in each state.
# Displays the result and offers the option to export it before returning the table.


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

# Calculates total quantity sold and total sales grouped by region and product.
# Creates a total sales column (quantity * sale_price) before building the pivot table.
# The pivot table shows how different products perform across regions for comparison.
# Prints the first part of the result and lets the user export it before returning it.
#
# AI HELP:
# - Wanted to sum up both quantity and total sales in the same pivot table
# - Asked: "How do I specify multiple value columns in a pandas pivot table 
#   and use sum for both?"
# - AI showed me values=["col1", "col2"] as a list which I didn't know you could do
# - I used this for my quantity/sales analysis and added the numeric conversion myself

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



# Summarizes total quantity sold and total sales grouped by customer type.
# Uses the computed total sales column to compare how different customer groups contribute.
# Converts values to numeric and rounds for readability before displaying.
# Shows the results and provides the option to export, then returns the pivot table.


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


# Finds the highest and lowest sale price within each product category.
# Uses a pivot table to compute both max and min values for easier comparison.
# Rounds results to two decimals to keep the output easy to read.
# Prints the results and offers the option to export before returning the table.



def analytic_7_max_min_unit_price_by_category(df: pd.DataFrame, label: str) -> pd.DataFrame:
    needed = {"product_category", "sale_price"}
    check_cols(df, needed)
    res = pd.pivot_table(df, index="product_category", values="sale_price", aggfunc=["max", "min"]).round(2)
    print(f"\n=== Max & min unit price by category {label} ===")
    print(res)
    try_export_df(res, f"max_min_unit_price_by_category_{label.strip('[]').replace('..','_')}")
    return res





# Counts how many different employees are associated with each sales region.
# Uses a pivot table with a unique count to avoid duplicates.
# Renames the output column to make the result clearer when printed.
# Displays the table and allows the user to export it before returning.


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


# Builds a custom pivot table based on user-selected rows, columns, value field, and aggregation.
# Works on a copy of the data so original values are not changed.
# Standardizes column names and adds a total_sales column when possible to support more pivot options.
# Used when the user wants to explore the data beyond the predefined analytics.
#
# AI HELP:
# - Wasn't sure if I should keep everything in one big function or split it up
# - Asked: "Is it better to have one large function or break pivot table 
#   creation into smaller helper functions?"
# - AI said to split things into smaller pieces which made sense
# - I used this advice to make _render_choices() and _pick_multi_from()
# - The whole wizard flow and how it works is my own design




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

# Main program loop that runs the dashboard interface.
# Loads the data first, then repeatedly shows the menu and waits for user input.
# Each menu choice runs one of the analytics or tools, and stores the result for later access.
# Supports quitting at any time, and includes error handling so the program doesn't crash.
# The stored results summary is shown before each menu to remind the user what they've already run.
# This function ties all other parts of the dashboard together.

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