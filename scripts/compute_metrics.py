import os, argparse, math, pandas as pd, numpy as np, yaml

def ann_vol(series, w, ANN): 
    if len(series) < w: return np.nan
    return series.rolling(w).std().iloc[-1] * ANN

def max_drawdown(ret):
    cum = ret.cumsum().apply(np.exp)
    dd = cum / cum.cummax() - 1
    return dd.min()

def CAGR(first_price, last_price, days):
    total = last_price/first_price - 1
    return (1+total)**(365/days)-1

def sortino(cagr, ret, ANN, rf=0.0):
    dn = ret[ret < 0].std() * ANN
    return np.nan if dn==0 or np.isnan(dn) else (cagr - rf)/dn

def calmar(cagr, mdd):
    return np.nan if mdd==0 else cagr/abs(mdd)

def var_cvar(ret, q=0.05):
    var = ret.quantile(q)
    cvar = ret[ret <= var].mean()
    return var, cvar

def amihud(ret, price, vol, window=30):
    dv = price*vol
    series = (ret.abs()/dv).rolling(window).mean()
    return series.iloc[-1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--raw", default="data/raw")
    parser.add_argument("--out", default="results")
    args = parser.parse_args()

    cfg = yaml.safe_load(open(args.config))
    syms = cfg["symbols"]; W = cfg["windows"]; ANN = math.sqrt(cfg["annualization_days"])
    q = 1 - cfg["risk_levels"][0]
    LWIN = cfg["liquidity_window"]

    rows = []
    for sym in syms:
        df = pd.read_csv(os.path.join(args.raw, f"{sym}.csv"), parse_dates=["date"], index_col="date")
        ret = np.log(df["price"]).diff().dropna()

        v30, v90, v180 = (ann_vol(ret, w, ANN) for w in W)
        mdd = max_drawdown(ret)
        days = (df.index[-1]-df.index[0]).days
        cagr = CAGR(df["price"].iloc[0], df["price"].iloc[-1], days)
        sor = sortino(cagr, ret, ANN)
        cal = calmar(cagr, mdd)
        var95, cvar95 = var_cvar(ret, q=0.05)
        illiq = amihud(ret, df["price"], df["volume"], window=LWIN)
        avg30_dvol = (df["price"]*df["volume"]).tail(30).mean()

        rows.append({
            "symbol": sym,
            "vol_30d_%": v30*100, "vol_90d_%": v90*100, "vol_180d_%": v180*100,
            "vol30/vol90": v30/v90 if pd.notna(v30) and pd.notna(v90) else np.nan,
            "vol30/vol180": v30/v180 if pd.notna(v30) and pd.notna(v180) else np.nan,
            "mdd_%": mdd*100, "cagr_%": cagr*100, "sortino": sor, "calmar": cal,
            "var95_%": var95*100, "cvar95_%": cvar95*100,
            "amihud_30d": illiq, "avg30d_dollar_vol": avg30_dvol
        })

    os.makedirs(args.out, exist_ok=True)
    pd.DataFrame(rows).round(4).to_csv(os.path.join(args.out, "metrics_summary.csv"), index=False)
    print("Saved results/metrics_summary.csv")
