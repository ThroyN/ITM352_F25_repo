import pandas as pd
import warnings

URL = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    df = pd.read_csv(
        URL,
        dtype_backend="pyarrow",
        on_bad_lines="skip",
        low_memory=False
    )


df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce', infer_datetime_format=True)

# Display result
print(df.head())
print(df.dtypes)
