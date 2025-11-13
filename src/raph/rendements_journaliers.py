from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent.parent
DATA_RAW = ROOT / 'data' / 'raw'
DATA_PROCESSED = ROOT / 'data' / 'processed'


def compute_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule le rendement journalier à partir d'un DataFrame contenant
    au minimum les colonnes : Date, Adj Close.
    Retourne : Date, Adj Close, Return
    """
    df = df.sort_values("Date")
    df["Return"] = df["Adj Close"].pct_change()
    return df[["Date", "Adj Close", "Return"]].dropna()


def main():
    tickers = pd.read_csv(DATA_PROCESSED / "selected_tickers.csv")
    records = []

    for _, row in tickers.iterrows():
        symbol = row["Symbol"]
        is_etf = row["ETF"]

        folder = "etfs" if is_etf == "Y" else "stocks"
        path = DATA_RAW / folder / f"{symbol}.csv"

        if not path.exists():
            print(f"WARNING: Missing file for {symbol}")
            continue

        df = pd.read_csv(path, usecols=["Date", "Adj Close"])
        df = compute_daily_returns(df)
        df["Symbol"] = symbol

        records.append(df)

    # Fusionner tous les tickers dans une seule table longue
    full = pd.concat(records, ignore_index=True)

    # Sauvegarde CSV classique
    full.to_csv(DATA_PROCESSED / "returns.csv", index=False)

    # Sauvegarde parquet (beaucoup plus rapide à recharger)
    full.to_parquet(DATA_PROCESSED / "returns.parquet", index=False)

    print("Done. Saved returns.csv and returns.parquet")


if __name__ == "__main__":
    main()
