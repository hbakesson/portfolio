import mstarpy
import yfinance as yf
import json
import datetime
import time
import pandas as pd
from datetime import timedelta
import warnings

warnings.filterwarnings('ignore')

isins = {
    "LU1681038243": "Amundi IS Nasdaq-100 Swap ETF",
    "SE0012454338": "Avanza Emerging Markets",
    "SE0001718388": "Avanza Zero",
    "SE0015811963": "Investor AB Class B",
    "SE0013282712": "Lysa Global Aktier Hållbar B",
    "SE0009268584": "Lysa Global Equity Broad C",
    "SE0009268394": "Lysa Räntor C",
    "SE0010323642": "PLUS Småbolag Sverige Index",
    "SE0023468905": "Protean Aktiesparfond Norden A",
    "SE0002593673": "SEB Sverige Indexnära A",
    "SE0000434201": "SEB Sverigefond Småbolag C/R",
    "SE0004297927": "Spiltan Aktiefond Investmentbolag",
    "SE0008613939": "Spiltan Globalfond Investmentbolag",
    "SE0000531881": "Storebrand Europa A SEK"
}

end_date = datetime.date.today()
start_date = end_date - timedelta(days=365*10)

all_data = {}

for isin, name in isins.items():
    print(f"Fetching {name} ({isin})...")
    time.sleep(1.5) # Sleep to respect API limits
    
    if isin == "SE0015811963":
        try:
            ticker = yf.Ticker("INVE-B.ST")
            hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            filtered_history = []
            if hist is not None and not hist.empty:
                for date, row in hist.iterrows():
                     if not pd.isna(row["Close"]) and row["Close"] > 0:
                         filtered_history.append({"date": date.strftime("%Y-%m-%d"), "nav": float(row["Close"])})
                
                monthly_data = {}
                for pt in filtered_history:
                    ym = pt["date"][:7]
                    monthly_data[ym] = pt
                    
                downsampled = list(monthly_data.values())
                downsampled.sort(key=lambda x: x["date"])
                
                if downsampled:
                    base_nav = downsampled[0]["nav"]
                    for pt in downsampled:
                        pt["normalized_nav"] = (pt["nav"] / base_nav) * 100
                    all_data[isin] = {"name": name, "data": downsampled}
                else:
                    print(f"No valid history found for {name} on yfinance")
            else:
                print(f"Empty history returned for {name}")
        except Exception as e:
            print(f"Failed pulling yfinance for {name}: {e}")
        continue
    
    country_code = "se"
    if isin.startswith("LU"):
        country_code = ""

    success = False
    for attempt in range(2):
        try:
            fund = mstarpy.Funds(term=isin, country=country_code)
            history = fund.nav(start_date=start_date, end_date=end_date)
            filtered_history = []
            if history:
                for point in history:
                    date_str = point.get("date")
                    val = point.get("nav")
                    if val is None:
                        val = point.get("totalReturn")
                    if date_str and val is not None:
                        filtered_history.append({"date": date_str[:10], "nav": float(val)})

                filtered_history.sort(key=lambda x: x["date"])
                
                monthly_data = {}
                for pt in filtered_history:
                    ym = pt["date"][:7]
                    monthly_data[ym] = pt
                
                downsampled = list(monthly_data.values())
                downsampled.sort(key=lambda x: x["date"])
                
                if downsampled:
                    base_nav = downsampled[0]["nav"]
                    for pt in downsampled:
                        pt["normalized_nav"] = (pt["nav"] / base_nav) * 100

                all_data[isin] = {"name": name, "data": downsampled}
                success = True
                break
        except Exception as e:
            if "401" in str(e):
                print(f"401 error. Will retry {name}...")
                time.sleep(3)
            else:
                print(f"Failed to fetch {name}: {e}")
                break
                
    if not success:
       print(f"Could not load data for {name} after retries")

with open("funds_data.json", "w") as f:
    json.dump(all_data, f)

print(f"Successfully processed {len(all_data)} funds!")
