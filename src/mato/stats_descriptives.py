"""Script utilitaire pour recalculer les statistiques descriptives et matrices.

Usage :
    python -m src.mato.stats_descriptives
"""

from __future__ import annotations

import argparse

import pandas as pd

from src import analysis
from src.paths import DATA_PROCESSED


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recalcule les KPIs descriptifs.")
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Liste optionnelle de tickers à traiter (sinon tous).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = analysis.compute_descriptive_stats(args.symbols)
    corr = analysis.correlation_matrix(args.symbols)

    stats_path = DATA_PROCESSED / "stats_summary.parquet"
    stats_csv = DATA_PROCESSED / "stats_summary.csv"
    corr_path = DATA_PROCESSED / "correlation_matrix.parquet"

    stats.to_parquet(stats_path, index=False)
    stats.to_csv(stats_csv, index=False)
    corr.to_parquet(corr_path)

    print(f"Statistiques exportées vers {stats_path.name} et {stats_csv.name}")
    print(f"Matrice de corrélation exportée vers {corr_path.name}")
    print(stats.head()[["Symbol", "mean_annual_return", "vol_annual", "return_risk_ratio"]])


if __name__ == "__main__":
    main()
