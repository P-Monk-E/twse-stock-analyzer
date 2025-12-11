import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

from twse_utils import screen_stock, annualized_return
from chart_utils import plot_candlestick_with_ma
from alert_rules import check_alerts, meets_criteria

st.set_page_config(page_title="TWSE Stock Analyzer", layout="wide")
st.title("📈 Taiwan Stock Analyzer")

st.sidebar.header("輸入查詢參數")
ticker = st.sidebar.text_input("請輸入台灣股票代號 (例如: 2618)", "2618")

end_date = datetime.today()
start_date = end_date - timedelta(days=365 * 10)

market_symbol = "^TWII"
mkt = yf.Ticker(market_symbol).history(start=start_date, end=end_date)
market_close = mkt["Close"]
rf = 0.01
market_return_annual = annualized_return(market_close)

if st.sidebar.button("🔍 查詢股票"):
    with st.spinner("正在分析中，請稍候..."):
        stock_data = screen_stock(ticker, market_close, rf, market_return_annual, start_date, end_date)

    if stock_data:
        st.subheader(f"📊 股票代號：{ticker}")
        st.markdown("---")

        try:
            t = yf.Ticker(f"{ticker}.TW")
            df = t.history(start=start_date, end=end_date)
            if not df.empty:
                fig = plot_candlestick_with_ma(df, title=f"{ticker} 技術圖")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"無法載入圖表: {e}")

        st.markdown("### 📋 財務指標")
        st.write(pd.DataFrame({
            "指標": [
                "負債權益比 (D/E)", "流動比率", "ROE", "Alpha",
                "Sharpe Ratio", "Beta", "中位偏離值 (MADR)"
            ],
            "數值": [
                round(stock_data["負債比"], 3),
                round(stock_data["流動比率"], 3),
                round(stock_data["ROE"], 3),
                round(stock_data["Alpha"], 3),
                round(stock_data["夏普值"], 3),
                round(stock_data["Beta"], 3),
                round(stock_data["10年中位偏離"], 4)
            ]
        }))

        alerts = check_alerts(stock_data)
        if alerts:
            st.error("⚠️ 警告條件未達標：")
            for a in alerts:
                st.markdown(f"- {a}")
        else:
            st.success("✅ 所有條件皆符合")

        if meets_criteria(stock_data):
            st.markdown("🏅 **此股票符合精選標準**")
        else:
            st.markdown("🚫 **此股票未達成所有選股條件**")
    else:
        st.warning("⚠️ 無法取得該股票資料或資料不足。")

