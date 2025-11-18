"""Selection de l'univers de titres à partir des métadonnées Kaggle.

Ce module filtre les tickers NASDAQ, calcule des métriques de liquidité et
conserve les combinaisons les plus actives pour alimenter le reste du projet.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd
from pandas import Timestamp

try:  # pragma: no cover - garde la compatibilité lorsque lancé hors package
    from .paths import DATA_PROCESSED, DATA_RAW
except ImportError:  # pragma: no cover
    from paths import DATA_PROCESSED, DATA_RAW


DEFAULT_END_DATE = Timestamp("2020-04-01")
DEFAULT_MIN_TRADING_DAYS = 252 * 3  # 3 années boursières de données utiles
DEFAULT_TOP_PER_BUCKET = 7
DEFAULT_MAX_SYMBOLS = 49


@dataclass
class SymbolSelection:
    """Résumé du profil de trading d'un ticker."""

    data_file: str
    total_volume: float
    average_volume: float
    trading_days: int
    first_date: Timestamp
    last_date: Timestamp

    def to_dict(self) -> dict:
        return {
            "DataFile": self.data_file,
            "TotalVolume": self.total_volume,
            "AverageVolume": self.average_volume,
            "TradingDays": self.trading_days,
            "FirstDate": self.first_date.date().isoformat(),
            "LastDate": self.last_date.date().isoformat(),
        }


def _candidate_filenames(symbol: str) -> Iterable[str]:
    upper = symbol.strip().upper()
    candidates = {
        upper,
        upper.replace(".", "-"),
        upper.replace(".", ""),
        upper.replace("$", "-"),
        upper.replace("/", "-"),
    }
    return candidates


def symbol_path(symbol: str, is_etf: bool) -> Optional[str]:
    folder = "etfs" if str(is_etf).upper() == "Y" else "stocks"
    for candidate in _candidate_filenames(symbol):
        rel = f"{folder}/{candidate}.csv"
        path = DATA_RAW / rel
        if path.exists():
            return rel
    return None


def summarize_symbol(path_str: str, end_date: Timestamp) -> Optional[SymbolSelection]:
    path = DATA_RAW / path_str
    df = pd.read_csv(path, usecols=["Date", "Adj Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[df["Date"] <= end_date]
    df = df.dropna(subset=["Adj Close", "Volume"])
    if df.empty:
        return None

    return SymbolSelection(
        data_file=path_str,
        total_volume=float(df["Volume"].sum()),
        average_volume=float(df["Volume"].mean()),
        trading_days=int(df.shape[0]),
        first_date=Timestamp(df["Date"].min()),
        last_date=Timestamp(df["Date"].max()),
    )


def load_metadata() -> pd.DataFrame:
    meta = pd.read_csv(DATA_RAW / "symbols_valid_meta.csv")
    # filtres décrits dans doc/schema.md
    mask = (
        (meta["Nasdaq Traded"] == "Y")
        & (meta["Test Issue"] == "N")
        & (meta["NextShares"] == "N")
    )
    financial_status = meta["Financial Status"].fillna("N")
    mask &= financial_status.isin(["", "N"])
    return meta[mask].copy()


def attach_activity_stats(meta: pd.DataFrame, end_date: Timestamp) -> pd.DataFrame:
    records = []
    for _, row in meta.iterrows():
        rel_path = symbol_path(row["Symbol"], row["ETF"])
        if rel_path is None:
            continue
        stats = summarize_symbol(rel_path, end_date)
        if stats is None:
            continue
        record = row.to_dict()
        record.update(stats.to_dict())
        records.append(record)
    return pd.DataFrame(records)


def select_top_tickers(
    enriched_meta: pd.DataFrame,
    *,
    top_per_bucket: int = DEFAULT_TOP_PER_BUCKET,
    min_trading_days: int = DEFAULT_MIN_TRADING_DAYS,
    max_symbols: int = DEFAULT_MAX_SYMBOLS,
) -> pd.DataFrame:
    eligible = enriched_meta[enriched_meta["TradingDays"] >= min_trading_days].copy()
    if eligible.empty:
        raise ValueError(
            "Aucun ticker ne satisfait les critères. Diminuer min_trading_days."
        )

    grouped = (
        eligible.sort_values("TotalVolume", ascending=False)
        .groupby(["Listing Exchange", "Market Category"], dropna=False, sort=True)
        .head(top_per_bucket)
        .reset_index(drop=True)
    )
    if grouped.empty:
        raise ValueError("Le regroupement n'a retourné aucun ticker.")

    if max_symbols:
        grouped = grouped.sort_values("TotalVolume", ascending=False).head(max_symbols)
    return grouped.sort_values(["Listing Exchange", "Market Category", "Symbol"])


def export_selection(df: pd.DataFrame) -> None:
    columns = [
        "Nasdaq Traded",
        "Symbol",
        "Security Name",
        "Listing Exchange",
        "Market Category",
        "ETF",
        "DataFile",
        "TradingDays",
        "FirstDate",
        "LastDate",
        "TotalVolume",
        "AverageVolume",
    ]
    df[columns].to_csv(DATA_PROCESSED / "selected_tickers.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sélectionne les tickers NASDAQ les plus liquides par catégorie."
    )
    parser.add_argument(
        "--end-date",
        type=Timestamp,
        default=DEFAULT_END_DATE,
        help="Dernier jour inclus pour l'historique (format YYYY-MM-DD).",
    )
    parser.add_argument(
        "--min-trading-days",
        type=int,
        default=DEFAULT_MIN_TRADING_DAYS,
        help="Nombre minimal de séances disponibles par ticker.",
    )
    parser.add_argument(
        "--top-per-bucket",
        type=int,
        default=DEFAULT_TOP_PER_BUCKET,
        help="Nombre de tickers à garder par combinaison Exchange x Category.",
    )
    parser.add_argument(
        "--max-symbols",
        type=int,
        default=DEFAULT_MAX_SYMBOLS,
        help="Nombre maximal total de tickers conservés.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    meta = load_metadata()
    enriched = attach_activity_stats(meta, args.end_date)
    selection = select_top_tickers(
        enriched,
        top_per_bucket=args.top_per_bucket,
        min_trading_days=args.min_trading_days,
        max_symbols=args.max_symbols,
    )
    export_selection(selection)
    print(
        f"{len(selection)} tickers conservés (min {args.min_trading_days} séances, "
        f"top {args.top_per_bucket} par groupe)."
    )


if __name__ == "__main__":
    main()
