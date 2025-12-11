import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import os
import sys

# ✅ 確保當前目錄可匯入本地模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ 只匯入存在的函數
from twse_utils import screen_stock, annualized_return
from chart_utils import plot_candlestick_with_ma
from alert_rules import check_alerts, meets_criteria

# ---------------- Streamlit App Config ----------------
st.set_page_config(page_title="TWSE Stock Analyzer", layout="wide")
st.title("📈 Taiwan Stock Analyzer")

st.sidebar.header("輸入查詢參數")
ticker = st.sidebar.text_input("請輸入台灣股票代號 (例如: 2618)", "2618")

end_date = datetime.today()
start_date = end_date - timedelta(days=365 * 10)

# ---------------- Market Benchmark ----------------
market_symbol = "^TWII"
market = yf.Ticker(market_symbol).history(start=start_date, end=end_date)
market_close = market["Close"]
rf = 0.01  # risk-free rate

# 計算市場報酬
market_return_annual = annualized_return(market_close)

# ---------------- User Action ----------------
if st.sidebar.button("🔍 查詢股票"):
    stock_data = screen_stock(ticker, market_close, rf, market_return_annual, start_date, end_date)

    if stock_data:
        st.subheader(f"📊 股票代號：{ticker}")

        # 技術圖表
        try:
            df = yf.Ticker(f"{ticker}.TW").history(start=start_date, end=end_date)
            fig = plot_candlestick_with_ma(df, title=f"{ticker} 技術圖")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"無法載入圖表: {e}")

        # 財務指標表
        st.markdown("### 📋 財務指標")
        st.write(pd.DataFrame({
            "指標": [
                "負債權益比 (D/E)", "流動比率", "ROE", "Alpha",
                "Sharpe Ratio", "Beta", "中位偏離值 (MADR)"
            ],
            "數值": [
                stock_data["負債比"],
                stock_data["流動比率"],
                stock_data["ROE"],
                stock_data["Alpha"],
                stock_data["夏普值"],
                stock_data["Beta"],
                stock_data["10年中位偏離"]
            ]
        }))

        # 警告提示
        alerts = check_alerts(stock_data)
        if alerts:
            st.error("⚠️ 警告條件未達標：")
            for a in alerts:
                st.write(f"🔔 {a}")
        else:
            st.success("✅ 所有條件皆符合")

        # 評估結論
        if meets_criteria(stock_data):
            st.info("🏅 符合所有選股條件")
        else:
            st.warning("📉 不符合所有選股條件")

    else:
        st.warning("⚠️ 找不到該股票或資料不足，請確認代碼正確")
