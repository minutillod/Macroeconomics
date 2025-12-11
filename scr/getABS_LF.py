import requests
import pandas as pd
from io import StringIO

# Base API endpoint
BASE_URL = "https://data.api.abs.gov.au/rest/data/ABS,LF,1.0.0/"
FORMAT = "format=csv"

# Define the labour Force series and descriptive names
SERIES = {
    # Original Series
    "M11.3.1599.10": "Working_Age_Population",
    "M10.3.1599.10": "Not_in_Labour_Force",
    "M9.3.1599.10": "Labour_Force",
    "M3.3.1599.10": "Employment",
    "M6.3.1599.10": "Unemployment",
    "M12.3.1599.10": "Participation_Rate",
    "M13.3.1599.10": "Unemployment_Rate",
    # Seasonally Adjusted Series (for Trend Data)
    "M1.3.1599.20": "Emp_SA_FT",
    "M2.3.1599.20": "Emp_SA_PT",
    "M3.3.1599.20": "Emp_SA_Total",
    "M12.1.1599.20": "PR_SA_Male",
    "M12.2.1599.20": "PR_SA_Female",
    "M12.3.1599.20": "PR_SA_Total",
    "M13.1.1599.20": "UR_SA_Male",
    "M13.2.1599.20": "UR_SA_Female",
    "M13.3.1599.20": "UR_SA_Total",
    }

def fetch_series(series_key):
    """Fetch one ABS LF series from the API and return a tidy DataFrame."""
    url = f"{BASE_URL}{series_key}.AUS.M?{FORMAT}"
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    df = df[["TIME_PERIOD", "OBS_VALUE"]]
    df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": SERIES[series_key]})
    return df

def main():
    print("Fetching ABS LF series…")

    # Download all datasets
    dfs = [fetch_series(k) for k in SERIES.keys()]

    # Merge on Date (outer join keeps all time periods)
    df_all = dfs[0]
    for d in dfs[1:]:
        df_all = pd.merge(df_all, d, on="Date", how="outer")

    # Sort chronologically and save
    df_all = df_all.sort_values("Date").reset_index(drop=True)

    # SCALE: Divide by 1000 to convert to millions
    for col in ["Working_Age_Population", "Not_in_Labour_Force", "Labour_Force", "Employment", "Unemployment", "Emp_SA_FT", "Emp_SA_PT", "Emp_SA_Total"]:
        if col in df_all.columns:
            df_all[col] = (df_all[col] / 1000)

    # SCALE: Divide by 100 to convert to rate
    for col in ["Participation_Rate", "Unemployment_Rate"]:
        if col in df_all.columns:
            df_all[col] = (df_all[col] / 100)

    df_all.to_csv("LF_monthly.csv", index=False)

    
    print("✅ Monthly data saved to 'LF_monthly.csv'")
    print(df_all.tail())

if __name__ == "__main__":
    main()
