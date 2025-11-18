"""Calcul des rendements journaliers et des prix normalisés pour les tickers sélectionnés."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from pandas import Timestamp

from ..paths import DATA_PROCESSED, DATA_RAW


DEFAULT_START_DATE = Timestamp("2010-01-01")
DEFAULT_END_DATE = Timestamp("2020-04-01")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Construit les tables de prix et rendements journaliers."
    )
    parser.add_argument(
        "--start-date",
        type=Timestamp,
        default=DEFAULT_START_DATE,
        help="Premier jour inclus (format YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        type=Timestamp,
        default=DEFAULT_END_DATE,
        help="Dernier jour inclus (format YYYY-MM-DD).",
    )
    return parser.parse_args()


def load_selection() -> pd.DataFrame:
    path = DATA_PROCESSED / "selected_tickers.csv"
    if not path.exists():
        raise FileNotFoundError(
            "selected_tickers.csv introuvable. Lancer `python -m src.data_loading` d'abord."
        )
    return pd.read_csv(path)


def resolve_data_path(row: pd.Series) -> Path:
    data_file = row.get("DataFile")
    if isinstance(data_file, str) and data_file:
        path = DATA_RAW / data_file
        if path.exists():
            return path

    folder = "etfs" if str(row["ETF"]).upper() == "Y" else "stocks"
    fallback = DATA_RAW / folder / f"{row['Symbol']}.csv"
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"Aucun fichier trouvé pour {row['Symbol']}")


def load_price_history(path: Path, start_date: Timestamp, end_date: Timestamp) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["Date", "Adj Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"])
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    df = df.loc[mask].sort_values("Date")
    df = df.dropna(subset=["Adj Close"])
    df["Adj Close"] = df["Adj Close"].astype(float)
    df["Volume"] = df["Volume"].fillna(0).astype(float)
    return df


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    returns = prices[["Date", "Adj Close"]].copy()
    returns["Return"] = returns["Adj Close"].pct_change()
    returns["Return"] = returns["Return"].replace([np.inf, -np.inf], np.nan)
    returns["Return"] = returns["Return"].clip(lower=-0.8, upper=0.8)
    return returns.dropna(subset=["Return"])


def build_tables(start_date: Timestamp, end_date: Timestamp) -> None:
    tickers = load_selection()
    price_frames: List[pd.DataFrame] = []
    return_frames: List[pd.DataFrame] = []

    for _, row in tickers.iterrows():
        try:
            path = resolve_data_path(row)
        except FileNotFoundError as exc:
            print(f"[WARN] {exc}")
            continue

        prices = load_price_history(path, start_date, end_date)
        if prices.empty:
            print(f"[WARN] Aucune donnée dans l'intervalle pour {row['Symbol']}")
            continue

        prices = prices.assign(
            Symbol=row["Symbol"],
            SecurityName=row["Security Name"],
            MarketCategory=row["Market Category"],
            ListingExchange=row["Listing Exchange"],
        )
        price_frames.append(prices)

        returns = compute_returns(prices)
        returns = returns.assign(Symbol=row["Symbol"])
        return_frames.append(returns[["Date", "Symbol", "Return"]])

    if not price_frames or not return_frames:
        raise RuntimeError("Impossible de construire les tables de prix/rendements.")

    prices_all = pd.concat(price_frames, ignore_index=True)
    prices_all["Normalized"] = prices_all.groupby("Symbol")["Adj Close"].transform(
        lambda s: (s / s.iloc[0]) * 100 if not s.empty else s
    )

    returns_long = pd.concat(return_frames, ignore_index=True)
    returns_long["Date"] = pd.to_datetime(returns_long["Date"])
    returns_long = returns_long.sort_values(["Date", "Symbol"])

    returns_wide = (
        returns_long.pivot(index="Date", columns="Symbol", values="Return")
        .sort_index()
    )
    returns_wide_full = returns_wide.dropna()

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    prices_all.to_parquet(DATA_PROCESSED / "prices.parquet", index=False)
    returns_long.to_parquet(DATA_PROCESSED / "returns_long.parquet", index=False)
    returns_long.to_csv(DATA_PROCESSED / "returns.csv", index=False)
    returns_wide.to_parquet(DATA_PROCESSED / "returns_wide.parquet")
    returns_wide_full.to_parquet(DATA_PROCESSED / "returns_wide_full.parquet")
    print(
        f"{len(prices_all.Symbol.unique())} tickers, "
        f"{prices_all['Date'].nunique()} séances conservés."
    )


def main() -> None:
    args = parse_args()
    build_tables(args.start_date, args.end_date)


if __name__ == "__main__":
    main()
