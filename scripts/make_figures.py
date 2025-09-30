import os, argparse, math, pandas as pd, numpy as np
import matplotlib.pyplot as plt

def plot_vol_rolling(sym, df, out, ANN):
    ret = np.log(df["price"]).diff()
    rv30  = ret.rolling(30).std()*ANN
    rv90  = ret.rolling(90).std()*ANN
    rv180 = ret.rolling(180).std()*ANN
    plt.figure(figsize=(8,4))
    plt.plot(rv180.index, rv180.values, label="Vol 180D")
    plt.plot(rv90.index,  rv90.values,  label="Vol 90D")
    plt.plot(rv30.index,  rv30.values,  label="Vol 30D")
    plt.title(f"{sym} — Rolling Annualized Volatility")
    plt.ylabel("Annualized Vol")
    plt.legend(); plt.tight_layout()
    os.makedirs(out, exist_ok=True)
    plt.savefig(os.path.join(out, f"{sym.lower()}_vol_rolling.png"), dpi=160)
    plt.close()

def plot_drawdown(sym, df, out):
    ret = np.log(df["price"]).diff().dropna()
    cum = ret.cumsum().apply(np.exp)
    dd = cum/cum.cummax()-1
    plt.figure(figsize=(8,4))
    plt.plot(dd.index, dd.values)
    plt.title(f"{sym} — Drawdown")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    os.makedirs(out, exist_ok=True)
    plt.savefig(os.path.join(out, f"{sym.lower()}_drawdown.png"), dpi=160)
    plt.close()

def plot_hist_var(sym, df, out):
    ret = np.log(df["price"]).diff().dropna()
    var95 = ret.quantile(0.05)
    cvar95 = ret[ret <= var95].mean()
    plt.figure(figsize=(8,4))
    plt.hist(ret.values, bins=60)
    plt.axvline(var95,  linestyle="--", label=f"VaR95={var95*100:.2f}%")
    plt.axvline(cvar95, linestyle=":",  label=f"CVaR95={cvar95*100:.2f}%")
    plt.title(f"{sym} — Returns Distribution with VaR/CVaR")
    plt.xlabel("Daily Log Return")
    plt.legend(); plt.tight_layout()
    os.makedirs(out, exist_ok=True)
    plt.savefig(os.path.join(out, f"{sym.lower()}_hist_var_cvar.png"), dpi=160)
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw")
    parser.add_argument("--out", default="results/figures")
    parser.add_argument("--symbols", nargs="+", default=["SOLUSDT","SUIUSDT","ETHUSDT"])
    parser.add_argument("--annualization_days", type=int, default=365)
    args = parser.parse_args()

    ANN = math.sqrt(args.annualization_days)
    for sym in args.symbols:
        df = pd.read_csv(os.path.join(args.raw, f"{sym}.csv"), parse_dates=["date"], index_col="date")
        plot_vol_rolling(sym, df, args.out, ANN)
        plot_drawdown(sym, df, args.out)
        plot_hist_var(sym, df, args.out)
    print("Saved figures to", args.out)
