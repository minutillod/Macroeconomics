import requests
import pandas as pd
from io import StringIO

# Base API endpoint
FORMAT = "format=csv"

# Define the six GDP series and descriptive names
SERIES = {
    "https://data.api.abs.gov.au/rest/data/ABS,ANA_EXP,1.0.0/DCH.GPM.SSS...Q": "GDP_Deflator",
    "https://data.api.abs.gov.au/rest/data/ABS,ANA_EXP,1.0.0/PCT_DCH.GPM.SSS...Q": "GDP_Deflator_Growth",
    "https://data.api.abs.gov.au/rest/data/ABS,CPI,2.0.0/1.10001..50.Q": "CPI",
    "https://data.api.abs.gov.au/rest/data/ABS,CPI,2.0.0/2.10001..50.Q": "CPI_Growth",
}

def fetch_series(series_key):
    """Fetch one ABS ANA_EXP / CPI series from the API and return a tidy DataFrame."""
    url = f"{series_key}?startPeriod=1960-Q1&{FORMAT}"
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    df = df[["TIME_PERIOD", "OBS_VALUE"]]
    df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": SERIES[series_key]})
    return df

def renormalize_to_base(df, column_name, base_period="2020-Q1"):
    """
    Create a new series normalized so that the value at base_period = 100.
    New series formula:
        X_t,new = X_t / X_base * 100
    """
    base_row = df.loc[df["Date"] == base_period, column_name]

    if base_row.empty:
        raise ValueError(f"Base period {base_period} not found for series '{column_name}'.")

    base_value = base_row.iloc[0]

    if pd.isna(base_value):
        raise ValueError(f"Base value for {column_name} at {base_period} is missing.")

    new_column_name = f"{column_name}_2020Q1_100"
    df[new_column_name] = df[column_name] / base_value * 100
    return df

def main():
    print("Fetching ABS Price Index series…")

    # Download all four datasets
    dfs = [fetch_series(k) for k in SERIES.keys()]

    # Merge on Date (outer join keeps all time periods)
    df_all = dfs[0]
    for d in dfs[1:]:
        df_all = pd.merge(df_all, d, on="Date", how="outer")

     # Sort chronologically
    df_all = df_all.sort_values("Date").reset_index(drop=True)

    # Renormalize GDP_Deflator and CPI to 2020-Q1 = 100
    df_all = renormalize_to_base(df_all, "GDP_Deflator", base_period="2020-Q1")
    df_all = renormalize_to_base(df_all, "CPI", base_period="2020-Q1")

    # Save to CSV
    df_all.to_csv("EXP_CPI_quarterly.csv", index=False)

    print("✅ Quarterly data saved to 'EXP_CPI_quarterly.csv'")
    print(df_all.tail())

if __name__ == "__main__":
    main()
