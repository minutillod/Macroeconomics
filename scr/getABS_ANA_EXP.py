import requests
import pandas as pd
from io import StringIO

# Base API endpoint
BASE_URL = "https://data.api.abs.gov.au/rest/data/ABS,ANA_EXP,1.0.0/VCH."
FORMAT = "format=csv"

# Define expenditure series and descriptive names
SERIES = {
    "GNE.SSS": "Real_GNE", # Gross National Expenditure.All Sectors
    "GPM.SSS": "Real_GDP", # Gross Domestic Product.All Sectors
    "FCE.PHS": "Consumption", # Final Consumption Expenditure.Private Sector
    "FCE.GGS": "Gov_Consumption", # Consumption.Public Sector
    "GFC.PSS": "Investment", # Gross Capital Formation.Private Sector
    "GFC.GGS": "Gov_Investment", # Investment.Public Sector
    "XGS.SSS": "Exports", # Exports of Goods and Services.All Sectors
    "MGS.SSS": "Imports", # Imports of Goods and Services.All Sectors
}

def fetch_series(series_key):
    """Fetch one ABS ANA_AGG series from the API and return a tidy DataFrame."""
    url = f"{BASE_URL}{series_key}.20..Q?{FORMAT}" # .20. is seasonally adjusted data
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
    print("Fetching ABS Expentiture series…")

    # Download all datasets
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

    # SCALE: Divide Nominal and Real GDP by 1000 to convert to billions
    # SCALE: Divide Nominal and Real GDP per capital by 100 to convert to thousands
    #for col in ["Nominal_GDP", "Real_GDP", "Nominal_GDP_per_capita", "Real_GDP_per_capita"]:
    #    if col in df_annual.columns:
    #        df_annual[col] = (df_annual[col] / 1000).round(2)

    # Calculate Real GDP per capita growth
    #if "Real_GDP_per_capita" in df_annual.columns:
    #    df_annual = calculate_growth_rate(
    #        df_annual,
    #        value_col="Real_GDP_per_capita",
    #        new_col="Real_GDP_per_capita_growth"
    #    )

    # Calculate Nominal GDP per capita growth
    #if "Nominal_GDP_per_capita" in df_annual.columns:
    #    df_annual = calculate_growth_rate(
    #        df_annual,
    #        value_col="Nominal_GDP_per_capita",
    #        new_col="Nominal_GDP_per_capita_growth"
    #    )

    df_annual = df_annual.sort_values("Year")
    df_annual.to_csv("ANA_EXP_annual.csv", index=False)

    print("✅ Annual data saved to 'ANA_EXP_annual.csv'")
    print(df_annual.tail())

if __name__ == "__main__":
    main()

