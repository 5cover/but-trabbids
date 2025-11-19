"""Pipeline unique pour générer toutes les données nécessaires au dashboard.

Étapes exécutées séquentiellement :
1. Sélection de l'univers de titres (metadata Nasdaq)
2. Construction des historiques prix/rendements pour 2010-01-04 → 2020-04-01
3. Calcul des statistiques descriptives (résumés + corrélations)

Commande unique : `python -m src.data_loading`
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from pandas import Timestamp

try:  # pragma: no cover
    from . import analysis
    from .paths import DATA_PROCESSED, DATA_RAW
except ImportError:  # pragma: no cover
    from src import analysis
    from paths import DATA_PROCESSED, DATA_RAW


DEFAULT_START_DATE = Timestamp("2010-01-01")
DEFAULT_END_DATE = Timestamp("2020-04-01")
DEFAULT_MIN_TRADING_DAYS = 252 * 3  # 3 ans utiles
DEFAULT_TOP_PER_BUCKET = 7
DEFAULT_MAX_SYMBOLS = 49
PROGRESS_BATCH_SIZE = 500


logger = logging.getLogger(__name__)


@dataclass
class SymbolProfile:
    symbol: str
    is_etf: bool
    data_file: str
    total_volume: float
    average_volume: float
    trading_days: int
    first_date: Timestamp
    last_date: Timestamp

    def to_dict(self) -> Dict[str, object]:
        return {
            "Symbol": self.symbol,
            "DataFile": self.data_file,
            "TotalVolume": self.total_volume,
            "AverageVolume": self.average_volume,
            "TradingDays": self.trading_days,
            "FirstDate": self.first_date.date().isoformat(),
            "LastDate": self.last_date.date().isoformat(),
        }


def _candidate_filenames(symbol: str) -> Iterable[str]:
    upper = symbol.strip().upper()
    yield from {
        upper,
        upper.replace(".", "-"),
        upper.replace(".", ""),
        upper.replace("$", "-"),
        upper.replace("/", "-"),
    }


def symbol_path(symbol: str, is_etf: str) -> Optional[str]:
    folder = "etfs" if str(is_etf).upper() == "Y" else "stocks"
    for candidate in _candidate_filenames(symbol):
        rel = f"{folder}/{candidate}.csv"
        if (DATA_RAW / rel).exists():
            return rel
    return None


def summarize_symbol(symbol: str, path_str: str, end_date: Timestamp) -> Optional[SymbolProfile]:
    path = DATA_RAW / path_str
    df = pd.read_csv(path, usecols=["Date", "Adj Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[df["Date"] <= end_date]
    df = df.dropna(subset=["Adj Close", "Volume"])
    if df.empty:
        return None
    return SymbolProfile(
        symbol=symbol,
        is_etf=False,
        data_file=path_str,
        total_volume=float(df["Volume"].sum()),
        average_volume=float(df["Volume"].mean()),
        trading_days=int(df.shape[0]),
        first_date=Timestamp(df["Date"].min()),
        last_date=Timestamp(df["Date"].max()),
    )


def load_metadata() -> pd.DataFrame:
    meta_path = DATA_RAW / "symbols_valid_meta.csv"
    logger.info("Chargement des métadonnées depuis %s", meta_path)
    meta = pd.read_csv(meta_path)
    mask = (
        (meta["Nasdaq Traded"] == "Y")
        & (meta["Test Issue"] == "N")
        & (meta["NextShares"] == "N")
    )
    financial_status = meta["Financial Status"].fillna("N")
    mask &= financial_status.isin(["", "N"])
    filtered = meta[mask].copy()
    logger.info("%s tickers admissibles après filtres", len(filtered))
    return filtered


def attach_activity_stats(meta: pd.DataFrame, end_date: Timestamp) -> pd.DataFrame:
    total_meta = len(meta)
    logger.info(
        "Calcul des métriques d'activité jusqu'au %s pour %s tickers",
        end_date.date().isoformat(),
        total_meta,
    )
    records = []
    for idx, (_, row) in enumerate(meta.iterrows(), start=1):
        rel_path = symbol_path(row["Symbol"], row["ETF"])
        if rel_path is None:
            continue
        stats = summarize_symbol(row["Symbol"], rel_path, end_date)
        if stats is None:
            continue
        record = row.to_dict()
        record.update(stats.to_dict())
        records.append(record)
        if total_meta and (idx % PROGRESS_BATCH_SIZE == 0 or idx == total_meta):
            logger.info("%s/%s tickers analysés", idx, total_meta)
    if not records:
        raise RuntimeError("Aucun ticker valide trouvé dans les métadonnées.")
    df = pd.DataFrame(records)
    logger.info("%s tickers disposent d'une série exploitable", len(df))
    return df


def select_top_tickers(
    enriched_meta: pd.DataFrame,
    *,
    top_per_bucket: int,
    min_trading_days: int,
    max_symbols: int,
) -> pd.DataFrame:
    eligible = enriched_meta[enriched_meta["TradingDays"] >= min_trading_days].copy()
    if eligible.empty:
        raise ValueError(
            "Aucun ticker ne satisfait min_trading_days. Diminuer la contrainte."
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
    grouped = grouped.sort_values(["Listing Exchange", "Market Category", "Symbol"])
    grouped.to_csv(DATA_PROCESSED / "selected_tickers.csv", index=False)
    print(f"[1/3] Sélection: {len(grouped)} tickers sauvegardés.")
    return grouped


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


def build_price_and_return_tables(
    selection: pd.DataFrame, start_date: Timestamp, end_date: Timestamp
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    price_frames: List[pd.DataFrame] = []
    return_frames: List[pd.DataFrame] = []

    total_symbols = len(selection)
    logger.info(
        "Construction des historiques pour %s tickers (%s → %s)",
        total_symbols,
        start_date.date().isoformat(),
        end_date.date().isoformat(),
    )

    for idx, (_, row) in enumerate(selection.iterrows(), start=1):
        try:
            path = resolve_data_path(row)
        except FileNotFoundError as exc:
            logger.warning("%s", exc)
            continue

        prices = load_price_history(path, start_date, end_date)
        if prices.empty:
            logger.warning("Aucune donnée dans l'intervalle pour %s", row["Symbol"])
            continue

        prices = prices.assign(
            Symbol=row["Symbol"],
            SecurityName=row["Security Name"],
            MarketCategory=row["Market Category"],
            ListingExchange=row["Listing Exchange"],
        )
        price_frames.append(prices)

        returns = compute_returns(prices)
        if returns.empty:
            continue
        returns = returns.assign(Symbol=row["Symbol"])
        return_frames.append(returns[["Date", "Symbol", "Return"]])

        if total_symbols and (idx % PROGRESS_BATCH_SIZE == 0 or idx == total_symbols):
            logger.info("%s/%s tickers traités pour les historiques", idx, total_symbols)

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
        returns_long.pivot(index="Date", columns="Symbol", values="Return").sort_index()
    )
    returns_wide_full = returns_wide.dropna()
    return prices_all, returns_long, returns_wide, returns_wide_full


def export_prices_and_returns(
    prices_all: pd.DataFrame,
    returns_long: pd.DataFrame,
    returns_wide: pd.DataFrame,
    returns_wide_full: pd.DataFrame,
) -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    prices_all.to_parquet(DATA_PROCESSED / "prices.parquet", index=False)
    returns_long.to_parquet(DATA_PROCESSED / "returns_long.parquet", index=False)
    returns_long.to_csv(DATA_PROCESSED / "returns.csv", index=False)
    returns_wide.to_parquet(DATA_PROCESSED / "returns_wide.parquet")
    returns_wide_full.to_parquet(DATA_PROCESSED / "returns_wide_full.parquet")
    unique = prices_all["Symbol"].nunique()
    sessions = prices_all["Date"].nunique()
    print(f"[2/3] Prix & rendements: {unique} tickers, {sessions} séances.")


def export_statistics() -> None:
    # Les fonctions d'analyse utilisent des caches → les vider avant recalcul
    analysis.load_selection.cache_clear()
    analysis.load_prices.cache_clear()
    analysis.load_returns_long.cache_clear()
    analysis.load_returns_wide.cache_clear()

    stats = analysis.compute_descriptive_stats()
    corr = analysis.correlation_matrix()
    stats_path = DATA_PROCESSED / "stats_summary.parquet"
    stats_csv = DATA_PROCESSED / "stats_summary.csv"
    corr_path = DATA_PROCESSED / "correlation_matrix.parquet"

    stats.to_parquet(stats_path, index=False)
    stats.to_csv(stats_csv, index=False)
    corr.to_parquet(corr_path)
    print(f"[3/3] Statistiques exportées ({len(stats)} lignes, corr {corr.shape}).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline complet : sélection + rendements + stats."
    )
    parser.add_argument(
        "--start-date",
        type=Timestamp,
        default=DEFAULT_START_DATE,
        help="Première date incluse pour les historiques (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        type=Timestamp,
        default=DEFAULT_END_DATE,
        help="Dernière date incluse pour les historiques (YYYY-MM-DD).",
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
        help="Nombre de tickers par combinaison Exchange x Market Category.",
    )
    parser.add_argument(
        "--max-symbols",
        type=int,
        default=DEFAULT_MAX_SYMBOLS,
        help="Nombre maximum total de tickers retenus.",
    )
    return parser.parse_args()


def run_pipeline(args: argparse.Namespace) -> None:
    if args.start_date >= args.end_date:
        raise ValueError("start_date doit être antérieure à end_date.")

    meta = load_metadata()
    enriched = attach_activity_stats(meta, args.end_date)
    selection = select_top_tickers(
        enriched,
        top_per_bucket=args.top_per_bucket,
        min_trading_days=args.min_trading_days,
        max_symbols=args.max_symbols,
    )
    prices_all, returns_long, returns_wide, returns_wide_full = (
        build_price_and_return_tables(selection, args.start_date, args.end_date)
    )
    export_prices_and_returns(prices_all, returns_long, returns_wide, returns_wide_full)
    export_statistics()
    print("Pipeline terminé. data/processed prêt pour le dashboard.")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    run_pipeline(parse_args())


if __name__ == "__main__":
    main()
