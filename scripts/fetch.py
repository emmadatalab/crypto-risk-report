import os, argparse, requests
import pandas as pd

def fetch_binance(symbol, interval="1d", limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    r = requests.get(url, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=20)
    r.raise_for_status()
    cols = ["open_time","open","high","low","close","volume","close_time","qav","trades","taker_base","taker_quote","ignore"]
    k = pd.DataFrame(r.json(), columns=cols)
    k["date"] = pd.to_datetime(k["open_time"], unit="ms", utc=True).dt.normalize()
    df = k.set_index("date")[["close","volume"]].astype(float).sort_index()
    df.columns = ["price","volume"]
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--out", default="data/raw")
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df = fetch_binance(args.symbol, args.interval, args.limit)
    df.to_csv(os.path.join(args.out, f"{args.symbol}.csv"))
    print(f"Saved {args.symbol} -> {args.out}")
