import requests
import pandas as pd
from io import StringIO

# Base API endpoint
BASE_URL = "https://data.api.abs.gov.au/rest/data/ABS,ANA_AGG,1.0.0/"
FORMAT = "format=csv"

# Define the six GDP series and descriptive names
SERIES = {
    "M1.GPM": "Real_GDP",
    "M3.GPM": "Nominal_GDP",
    "M1.GPM_PCA": "Real_GDP_per_capita",
    "M3.GPM_PCA": "Nominal_GDP_per_capita",
    "M2.GPM_PCA": "Real_GDP_per_capita_growth",
    # "M4.GPM_PCA": "Nominal_GDP_per_capita_growth"
}

def fetch_series(series_key):
    """Fetch one ABS ANA_AGG series from the API and return a tidy DataFrame."""
    url = f"{BASE_URL}{series_key}.10..Q?{FORMAT}"
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    df = df[["TIME_PERIOD", "OBS_VALUE"]]
    df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": SERIES[series_key]})
    return df

def aggregate_quarters_to_annual(df, col_name):
    # Extract year and quarter
    df["Year"] = df["Date"].str.extract(r"(\d{4})").astype(int)
    df["Quarter"] = df["Date"].str.extract(r"Q([1-4])").astype(int)

    # Map each quarter to its financial year
    df["Financial_Year"] = df["Year"]
    df.loc[df["Quarter"].isin([3, 4]), "Financial_Year"] = df["Year"] + 1

    # Count how many quarters per FY
    quarters_per_fy = df.groupby("Financial_Year")["Quarter"].nunique()

    # Keep only full FYs with 4 quarters
    full_fys = quarters_per_fy[quarters_per_fy == 4].index
    df_full = df[df["Financial_Year"].isin(full_fys)]

    # Sum quarterly values into FY totals
    df_fy = (
        df_full.groupby("Financial_Year", as_index=False)[col_name]
        .sum()
        .round(2)
    )

    df_fy.rename(columns={"Financial_Year": "Year"}, inplace=True)
    return df_fy

def calculate_growth_rate(df, value_col, new_col):
    df = df.copy()
    df[new_col] = df[value_col].pct_change() * 100
    df[new_col] = df[new_col].round(2)
    return df

def main():
    print("Fetching ABS GDP series…")

    # Download all six datasets
    dfs = [fetch_series(k) for k in SERIES.keys()]

    # Merge on Date (outer join keeps all time periods)
    df_all = dfs[0]
    for d in dfs[1:]:
        df_all = pd.merge(df_all, d, on="Date", how="outer")

    # Sort chronologically and save
    df_all = df_all.sort_values("Date").reset_index(drop=True)
    # df_all.to_csv("GDP.csv", index=False)

    # print("\n✅ Combined data saved to 'GDP.csv'")
    # print(df_all.tail())

    # Convert each series to annual totals
    annual_dfs = []
    for col in [SERIES[k] for k in SERIES.keys()]:
        annual_dfs.append(aggregate_quarters_to_annual(df_all[["Date", col]].dropna(), col))

    # Merge all annual series
    df_annual = annual_dfs[0]
    for d in annual_dfs[1:]:
        df_annual = pd.merge(df_annual, d, on="Year", how="outer")

    # Calculate Nominal GDP per capita growth
    if "Nominal_GDP_per_capita" in df_annual.columns:
        df_annual = calculate_growth_rate(
            df_annual,
            value_col="Nominal_GDP_per_capita",
            new_col="Nominal_GDP_per_capita_growth"
        )

    df_annual = df_annual.sort_values("Year")
    df_annual.to_csv("GDP_annual.csv", index=False)

    print("✅ Annual data saved to 'GDP_annual.csv'")
    print(df_annual.tail())

if __name__ == "__main__":
    main()
