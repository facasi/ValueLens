import math

def dcf_per_share(fcf, growth, discount, terminal_growth, years, shares, net_debt=0):
    if not all(math.isfinite(float(v)) for v in (fcf,growth,discount,terminal_growth,shares,net_debt)) or shares<=0 or discount<=terminal_growth or years<1:
        return None
    projected=fcf
    pv=0.0
    for year in range(1,years+1):
        projected *= 1+growth
        pv += projected/(1+discount)**year
    terminal=projected*(1+terminal_growth)/(discount-terminal_growth)
    return (pv+terminal/(1+discount)**years-net_debt)/shares

def score(pe, forward_pe, roe, roic, debt_to_equity, fcf, margin):
    parts=[]
    for val, good, maximum in [(pe, lambda x: 0<x<=20, 20),(forward_pe,lambda x:0<x<=18,15),(roe,lambda x:x>=0.15,15),(roic,lambda x:x>=0.12,15),(debt_to_equity,lambda x:x<=80,10),(fcf,lambda x:x>0,15),(margin,lambda x:x>=0.25,10)]:
        if val is not None:
            parts.append((maximum if good(val) else 0,maximum))
    return (round(100*sum(p for p,_ in parts)/sum(w for _,w in parts)),len(parts)) if parts else (None,0)
