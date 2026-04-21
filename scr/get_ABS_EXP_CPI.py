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
    url = f"{series_key}?{FORMAT}"
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    df = df[["TIME_PERIOD", "OBS_VALUE"]]
    df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": SERIES[series_key]})
    return df

def main():
    print("Fetching ABS Price Index series…")

    # Download all four datasets
    dfs = [fetch_series(k) for k in SERIES.keys()]

    # Merge on Date (outer join keeps all time periods)
    df_all = dfs[0]
    for d in dfs[1:]:
        df_all = pd.merge(df_all, d, on="Date", how="outer")

    # Sort chronologically and save
    df_all = df_all.sort_values("Date").reset_index(drop=True)

    df_all.to_csv("EXP_CPI_quarterly.csv", index=False)

    print("✅ Quarterly data saved to 'EXP_CPI_quarterly.csv'")
    print(df_all.tail())
if __name__ == "__main__":
    main()
