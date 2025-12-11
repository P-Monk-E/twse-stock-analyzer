def check_alerts(stock):
    alerts=[]
    if stock["負債比"]>0.5: alerts.append("❗ Debt/Equity too high")
    if not (1.25<=stock["流動比率"]<=2.75):
        alerts.append("❗ Current Ratio out of range")
    if stock["ROE"]<0.08: alerts.append("❗ ROE below threshold")
    if stock["Alpha"]<0: alerts.append("❗ Alpha negative")
    if stock["Alpha"]>0.5: alerts.append("⚡ Alpha strong!")
    return alerts

def meets_criteria(stock):
    return (stock["負債比"]<=0.5 and
            1.25<=stock["流動比率"]<=2.75 and
            stock["ROE"]>=0.08 and
            stock["Alpha"]>0)
