import json
import datetime
from datetime import timedelta
import random
import math

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

# base returns and volatility based on market logic
market_profiles = {
    "LU1681038243": {"return": 0.18, "vol": 0.20}, # Tech ETF (Nasdaq) high return, high vol
    "SE0012454338": {"return": 0.06, "vol": 0.22}, # EM, lower return past 10y, high vol
    "SE0001718388": {"return": 0.09, "vol": 0.15}, # Sweden large cap
    "SE0015811963": {"return": 0.15, "vol": 0.18}, # Investor AB, high return
    "SE0013282712": {"return": 0.10, "vol": 0.14}, # Global sustainable
    "SE0009268584": {"return": 0.10, "vol": 0.14}, # Global equity broad
    "SE0009268394": {"return": 0.02, "vol": 0.03}, # Fixed income / Rates
    "SE0010323642": {"return": 0.12, "vol": 0.20}, # Sweden small cap
    "SE0023468905": {"return": 0.11, "vol": 0.16}, # Nordic equity
    "SE0002593673": {"return": 0.09, "vol": 0.15}, # SEB Sweden index
    "SE0000434201": {"return": 0.12, "vol": 0.20}, # SEB Sweden small cap
    "SE0004297927": {"return": 0.16, "vol": 0.18}, # Spiltan Investmentbolag
    "SE0008613939": {"return": 0.12, "vol": 0.16}, # Spiltan Global Investmentbolag
    "SE0000531881": {"return": 0.07, "vol": 0.15}, # Europe large cap
}

all_data = {}
start_date = datetime.date(2016, 2, 27)
end_date = datetime.date(2026, 2, 27)

num_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

# Global market shock in 2020 (Covid) and 2022 (Inflation)
def apply_shocks(month_idx):
    if 48 <= month_idx <= 50: # Covid crash (early 2020)
        return -0.05
    if 51 <= month_idx <= 60: # Covid bounce
        return +0.02
    if 72 <= month_idx <= 84: # 2022 downturn
        return -0.015
    return 0

for isin, name in isins.items():
    prof = market_profiles.get(isin, {"return": 0.08, "vol": 0.15})
    annual_return = prof["return"]
    annual_vol = prof["vol"]
    
    monthly_ret = annual_return / 12
    monthly_vol = annual_vol / math.sqrt(12)
    
    current_nav = 100.0
    fund_history = []
    
    current_date = start_date
    for i in range(num_months + 1):
        # Store
        fund_history.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "nav": round(current_nav, 2),
            "normalized_nav": round(current_nav, 2)
        })
        
        # Calculate next step
        shock = apply_shocks(i) if prof["vol"] > 0.05 else apply_shocks(i) * 0.2
        random_shock = random.gauss(0, monthly_vol)
        
        # step nav
        current_nav = current_nav * (1 + monthly_ret + random_shock + shock)
        if current_nav < 10:
            current_nav = 10
            
        # increment month
        m = current_date.month
        y = current_date.year
        if m == 12:
            current_date = datetime.date(y + 1, 1, 27)
        else:
            current_date = datetime.date(y, m + 1, 27)
            
    all_data[isin] = {
        "name": name,
        "data": fund_history
    }

js_content = f"const fundsData = {json.dumps(all_data)};"
with open("data.js", "w") as f:
    f.write(js_content)

print("Generated mocked data to data.js")
