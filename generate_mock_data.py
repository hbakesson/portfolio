import json
import datetime
from datetime import timedelta
import random
import math

isins_portfolj = {
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

isins_prospects = isins_portfolj.copy()

market_profiles = {
    "LU1681038243": {"return": 0.18, "vol": 0.20}, 
    "SE0012454338": {"return": 0.06, "vol": 0.22},
    "SE0001718388": {"return": 0.09, "vol": 0.15},
    "SE0015811963": {"return": 0.15, "vol": 0.18},
    "SE0013282712": {"return": 0.10, "vol": 0.14},
    "SE0009268584": {"return": 0.10, "vol": 0.14},
    "SE0009268394": {"return": 0.02, "vol": 0.03},
    "SE0010323642": {"return": 0.12, "vol": 0.20},
    "SE0023468905": {"return": 0.11, "vol": 0.16},
    "SE0002593673": {"return": 0.09, "vol": 0.15},
    "SE0000434201": {"return": 0.12, "vol": 0.20},
    "SE0004297927": {"return": 0.16, "vol": 0.18},
    "SE0008613939": {"return": 0.12, "vol": 0.16},
    "SE0000531881": {"return": 0.07, "vol": 0.15},
}

def apply_shocks(total_days, current_day):
    m = (current_day / total_days) * 120
    if 48 <= m <= 50:
        return -0.05 / 21
    if 51 <= m <= 60:
        return +0.02 / 21
    if 72 <= m <= 84:
        return -0.015 / 21
    return 0

end_date = datetime.date(2026, 2, 27)
start_date = end_date - timedelta(days=365*10)

def generate_fund_history(isin, name, variant_seed):
    random.seed(isin + variant_seed) # ensures deterministic but different by watchlist if needed
    prof = market_profiles.get(isin, {"return": 0.08, "vol": 0.15})
    annual_return = prof["return"]
    annual_vol = prof["vol"]
    
    daily_ret = annual_return / 252
    daily_vol = annual_vol / math.sqrt(252)
    
    current_nav = 100.0
    fund_history = []
    
    current_date = start_date
    days_count = (end_date - start_date).days
    trading_days = sum(1 for d in range(days_count + 1) if (start_date + timedelta(days=d)).weekday() < 5)
    
    td_passed = 0
    for i in range(days_count + 1):
        if current_date.weekday() < 5:
            fund_history.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "nav": round(current_nav, 2)
            })
            
            shock = apply_shocks(trading_days, td_passed) if prof["vol"] > 0.05 else apply_shocks(trading_days, td_passed) * 0.2
            random_shock = random.gauss(0, daily_vol)
            
            # small variance between lists so they don't look exactly identical even if holdings are identical
            if variant_seed == "prospects":
                 random_shock *= 1.05 

            current_nav = current_nav * (1 + daily_ret + random_shock + shock)
            if current_nav < 10:
                current_nav = 10
            td_passed += 1
            
        current_date += timedelta(days=1)
        
    return {"name": name, "data": fund_history}

data_export = {
    "Portfölj": {k: generate_fund_history(k, v, "portfolj") for k, v in isins_portfolj.items()},
    "Prospects": {k: generate_fund_history(k, v, "prospects") for k, v in isins_prospects.items()}
}

js_content = f"const fundsData = {json.dumps(data_export)};"
with open("data.js", "w") as f:
    f.write(js_content)

print("Generated full daily resolution mock data for Portfölj and Prospects.")
