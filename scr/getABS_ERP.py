import requests
import pandas as pd
from io import StringIO

# Base API endpoint
BASE_URL = "https://data.api.abs.gov.au/rest/data/ABS,ERP_Q,1.0.0/"
FORMAT = "format=csv"

# Define the labour Force series and descriptive names
SERIES = {
    # Original Series
    "1.3.TOT": "Estimated_Resident_Population",
    }

def fetch_series(series_key):
    """Fetch one ABS LF series from the API and return a tidy DataFrame."""
    url = f"{BASE_URL}{series_key}.AUS.Q?{FORMAT}"
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    df = df[["TIME_PERIOD", "OBS_VALUE"]]
    df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": SERIES[series_key]})
    return df

def main():
    print("Fetching ABS ERP_Q series…")

    # Download all datasets
    dfs = [fetch_series(k) for k in SERIES.keys()]

    # # Merge on Date (outer join keeps all time periods)
    df_all = dfs[0]
    for d in dfs[1:]:
        df_all = pd.merge(df_all, d, on="Date", how="outer")

    # Sort chronologically and save
    df_all = df_all.sort_values("Date").reset_index(drop=True)

    # SCALE: Divide by 1,000,000 to convert to millions
    for col in ["Estimated_Resident_Population"]:
        if col in df_all.columns:
            df_all[col] = (df_all[col] / 1000000)

    df_all.to_csv("ERP_quarterly.csv", index=False)

    
    print("✅ Quarterly data saved to 'ERP_quarterly.csv'")
    print(df_all.tail())

if __name__ == "__main__":
    main()
