import pandas as pd
import numpy as np
import yfinance as yf
import statsmodels.api as sm
from datetime import datetime

def get_twse_stock_codes():
    return []

def fetch_price_data(code, start, end):
    symbol = f"{code}.TW"
    t = yf.Ticker(symbol)
    df = t.history(start=start, end=end)
    return (df if not df.empty else None), t

def annualized_return(prices):
    r = prices.pct_change().dropna()
    return (1 + r.mean()) ** 252 - 1 if not r.empty else np.nan

def calc_beta(prices_asset, prices_market):
    df = pd.concat([prices_asset, prices_market], axis=1).dropna()
    if df.empty:
        return np.nan
    df.columns = ["asset","market"]
    am = df["asset"].resample("M").last().pct_change().dropna()
    mm = df["market"].resample("M").last().pct_change().dropna()
    if len(am) < 12:
        return np.nan
    X = sm.add_constant(mm)
    model = sm.OLS(am, X).fit()
    return float(model.params["market"])

def calc_alpha(prices_asset, prices_market, rf):
    df = pd.concat([prices_asset, prices_market], axis=1).dropna()
    ar = df.iloc[:, 0].pct_change().dropna()
    mr = df.iloc[:, 1].pct_change().dropna()
    excess_a = ar - rf/252
    excess_m = mr - rf/252
    X = sm.add_constant(excess_m)
    model = sm.OLS(excess_a, X).fit()
    return float(model.params["const"]) * 252

def calc_sharpe(prices, rf):
    r = prices.pct_change().dropna()
    if r.std() == 0:
        return np.nan
    return ((r - rf/252).mean()/r.std()) * np.sqrt(252)

def screen_stock(code, market_close, rf, mr, start, end):
    prices, t = fetch_price_data(code, start, end)
    if prices is None:
        return None
    beta = calc_beta(prices["Close"], market_close)
    alpha = calc_alpha(prices["Close"], market_close, rf)
    sharpe = calc_sharpe(prices["Close"], rf)
    try:
    info = t.info
    except:
    info = {}
    total_liab = info.get("totalLiab", np.nan)
    equity = info.get("totalStockholderEquity", np.nan)
    debt_equity = total_liab/equity if equity and not np.isnan(equity) else np.nan
    current_ratio = info.get("currentRatio", np.nan)
    roe = info.get("returnOnEquity", np.nan)
    returns = prices["Close"].pct_change().dropna()
    median_dev = np.median(np.abs(returns - returns.mean())) if not returns.empty else np.nan

    return {"負債比":debt_equity,"流動比率":current_ratio,"ROE":roe,
            "Alpha":alpha,"夏普值":sharpe,"Beta":beta,"10年中位偏離":median_dev}

