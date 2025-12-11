def screen_stock(code, market_close, rf, market_return_annual, start, end):
    import numpy as np
    prices, t = fetch_price_data(code, start, end)
    if prices is None or "Close" not in prices:
        return None

    # 計算 Beta、Alpha、Sharpe
    beta = calc_beta(prices["Close"], market_close)
    alpha = calc_alpha(prices["Close"], market_close, rf)
    sharpe = calc_sharpe(prices["Close"], rf)

    # 財報資訊
    info = t.info if hasattr(t, "info") else {}

    total_liab = info.get("totalLiab", np.nan)
    total_assets = info.get("totalAssets", np.nan)
    current_ratio = info.get("currentRatio", np.nan)
    roe = info.get("returnOnEquity", np.nan)

    # ✅ 自行計算負債權益比（替代方案）
    if total_assets and total_liab and not np.isnan(total_assets) and not np.isnan(total_liab):
        equity = total_assets - total_liab
        if equity != 0:
            debt_equity = total_liab / equity
        else:
            debt_equity = np.nan
    else:
        debt_equity = np.nan

    # 中位偏離值
    returns = prices["Close"].pct_change().dropna()
    median_dev = np.median(np.abs(returns - returns.mean())) if not returns.empty else np.nan

    return {
        "負債比": debt_equity,
        "流動比率": current_ratio,
        "ROE": roe,
        "Alpha": alpha,
        "夏普值": sharpe,
        "Beta": beta,
        "10年中位偏離": median_dev
    }
