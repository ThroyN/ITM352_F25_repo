import pandas as pd
import warnings

URL = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"
LOCAL_FALLBACK = "sales_data.csv"

def read_sales_data(url: str = URL, local_path: str = LOCAL_FALLBACK) -> pd.DataFrame:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            df = pd.read_csv(
                url,
                dtype_backend="pyarrow",
                on_bad_lines="skip",
                low_memory=False
            )
            source = url
        except Exception as e:
            print(f"[Info] Primary read failed: {e}\n[Info] Falling back to local file: {local_path}")
            df = pd.read_csv(
                local_path,
                dtype_backend="pyarrow",
                on_bad_lines="skip",
                low_memory=False
            )
            source = local_path

        if caught:
            print("\n[Warnings captured during read_csv]:")
            for w in caught:
                print(f" - {w.category.__name__}: {w.message}")

        print(f"\n[Loaded from]: {source}")
        return df

df = read_sales_data()
print("\n[Head]")
print(df.head())
print("\n[Dtypes]")
print(df.dtypes)
