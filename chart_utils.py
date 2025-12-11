import plotly.graph_objects as go

def plot_candlestick_with_ma(df, title=""):
    df["MA5"]  = df["Close"].rolling(5).mean()
    df["MA10"] = df["Close"].rolling(10).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
                                 low=df["Low"], close=df["Close"], name="Price"))

    for ma, col in [("MA5","blue"),("MA10","green"),("MA20","orange")]:
        fig.add_trace(go.Scatter(x=df.index,y=df[ma],mode="lines",name=ma,
                                 line=dict(color=col)))
    fig.update_layout(title=title,xaxis_title="Date",yaxis_title="Price")
    return fig
