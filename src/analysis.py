"""Fonctions utilitaires pour statistiques descriptives et optimisation de portefeuille.

Ce module sert de pont entre :
- les fichiers produits par `src.data_loading` (lecture avec cache),
- l'app Dash (qui a besoin d'un accès simple aux KPI et au modèle Markowitz),
- les scripts CLI éventuels.

Chaque fonction est volontairement “friendly” : on explicite ce qui est calculé.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, Sequence

import cvxpy as cp
import numpy as np
import pandas as pd

from .paths import DATA_PROCESSED

@lru_cache(maxsize=None)
def load_prices() -> pd.DataFrame:
    """Chargement paresseux des prix normalisés.

    Les caches évitent de relire plusieurs centaines de Mo à chaque Callback Dash.
    """
    df = pd.read_parquet(DATA_PROCESSED / "prices.parquet")
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values(["Symbol", "Date"]).reset_index(drop=True)


@lru_cache(maxsize=None)
def load_returns_long() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PROCESSED / "returns_long.parquet")
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values(["Date", "Symbol"]).reset_index(drop=True)


@lru_cache(maxsize=None)
def load_returns_wide() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PROCESSED / "returns_wide.parquet")
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


@lru_cache(maxsize=None)
def load_selection() -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / "selected_tickers.csv")


def compute_descriptive_stats(symbols: Iterable[str] | None = None) -> pd.DataFrame:
    """Assemble les KPIs nécessaires aux tableaux/graphes du dashboard."""
    returns = load_returns_wide()
    if symbols:
        returns = returns[list(symbols)]

    selection = load_selection().set_index("Symbol")
    prices = load_prices()
    group_prices = prices.groupby("Symbol")

    mean_daily = returns.mean()
    vol_daily = returns.std()
    trading_days = group_prices.size()
    first_price = group_prices["Adj Close"].first()
    last_price = group_prices["Adj Close"].last()
    avg_volume = group_prices["Volume"].mean()
    total_volume = group_prices["Volume"].sum()
    first_date = group_prices["Date"].first()
    last_date = group_prices["Date"].last()

    stats = pd.DataFrame(
        {
            "mean_daily_return": mean_daily,
            "vol_daily": vol_daily,
            "mean_annual_return": ((1 + mean_daily) ** 252) - 1,
            "vol_annual": vol_daily * np.sqrt(252),
        }
    )
    stats["return_risk_ratio"] = stats["mean_annual_return"] / stats["vol_annual"]
    stats["cumulative_return"] = (last_price / first_price) - 1
    stats["trading_days"] = trading_days
    stats["avg_volume"] = avg_volume
    stats["total_volume"] = total_volume
    stats["start_date"] = first_date.dt.date
    stats["end_date"] = last_date.dt.date

    stats = stats.join(selection, how="left")
    stats = stats.reset_index().rename(columns={"index": "Symbol"})
    stats = stats.sort_values("return_risk_ratio", ascending=False)
    return stats


def correlation_matrix(symbols: Sequence[str] | None = None) -> pd.DataFrame:
    returns = load_returns_wide()
    if symbols:
        returns = returns[list(symbols)]
    corr = returns.corr()
    if not corr.empty:
        np.fill_diagonal(corr.values, 1.0)
    return corr


def prepare_returns(symbols: Sequence[str]) -> pd.DataFrame:
    returns = load_returns_wide()
    missing = [s for s in symbols if s not in returns.columns]
    if missing:
        raise KeyError(f"Tickers inconnus: {missing}")
    subset = returns[list(symbols)].dropna()
    if subset.empty:
        raise ValueError("Pas assez de données après suppression des valeurs manquantes.")
    return subset


@dataclass
class PortfolioSolution:
    symbols: List[str]
    weights: pd.Series
    expected_return_daily: float
    expected_return_annual: float
    volatility_daily: float
    volatility_annual: float
    ratio: float

    def to_dict(self) -> dict:
        return {
            "expected_return_daily": self.expected_return_daily,
            "expected_return_annual": self.expected_return_annual,
            "volatility_daily": self.volatility_daily,
            "volatility_annual": self.volatility_annual,
            "ratio": self.ratio,
            "weights": self.weights.to_dict(),
        }


@dataclass
class MarkowitzModel:
    """Petit emballage autour de cvxpy pour garder le code Dash lisible."""
    symbols: List[str]
    returns: pd.DataFrame
    mean_daily: np.ndarray
    cov_matrix: np.ndarray

    @classmethod
    def from_symbols(cls, symbols: Sequence[str]) -> "MarkowitzModel":
        subset = prepare_returns(symbols)
        mean_daily = subset.mean().values
        cov = subset.cov().values + np.eye(len(symbols)) * 1e-8
        return cls(list(symbols), subset, mean_daily, cov)

    def optimize(
        self,
        target_annual_return: float | None = None,
        allow_short: bool = False,
        max_weight: float | None = 0.35,
        solver=cp.CLARABEL,
    ) -> PortfolioSolution:
        n = len(self.symbols)
        w = cp.Variable(n)
        constraints = [cp.sum(w) == 1]
        if not allow_short:
            constraints.append(w >= 0)

        weight_cap = max_weight if (max_weight is not None and n > 1) else None
        if weight_cap is not None:
            constraints.append(w <= weight_cap)

        if target_annual_return is not None:
            target_daily = (1 + target_annual_return) ** (1 / 252) - 1
            constraints.append(self.mean_daily @ w >= target_daily)

        objective = cp.Minimize(cp.quad_form(w, self.cov_matrix))
        prob = cp.Problem(objective, constraints)
        prob.solve(solver=solver, verbose=False)

        if w.value is None:
            raise RuntimeError(f"Optimisation échouée ({prob.status}).")

        weights = np.array(w.value).reshape(-1)
        weights = np.clip(weights, 0, None) if not allow_short else weights
        weights = weights / weights.sum()
        return self._build_solution(weights)

    def minimum_variance(
        self,
        allow_short: bool = False,
        max_weight: float | None = 0.35,
        solver=cp.CLARABEL,
    ) -> PortfolioSolution:
        return self.optimize(
            target_annual_return=None,
            allow_short=allow_short,
            max_weight=max_weight,
            solver=solver,
        )

    def efficient_frontier(
        self,
        num_points: int = 25,
        allow_short: bool = False,
        max_weight: float | None = 0.35,
        solver=cp.CLARABEL,
    ) -> List[PortfolioSolution]:
        """Prépare les points de la courbe bleue (frontière) affichée dans Dash."""
        annual_returns = self.mean_daily * 252
        low = float(np.percentile(annual_returns, 10))
        high = float(np.percentile(annual_returns, 90))
        if np.isclose(low, high):
            high = low + 0.05

        targets = np.linspace(low, high, num_points)
        solutions: List[PortfolioSolution] = []
        for target in targets:
            try:
                sol = self.optimize(
                    target_annual_return=target,
                    allow_short=allow_short,
                    max_weight=max_weight,
                    solver=solver,
                )
                solutions.append(sol)
            except Exception as exc:
                print(f"[WARN] frontier target {target:.4f}: {exc}")
        return solutions

    def _build_solution(self, weights: np.ndarray) -> PortfolioSolution:
        expected_return_daily = float(self.mean_daily @ weights)
        expected_return_annual = float((1 + expected_return_daily) ** 252 - 1)
        volatility_daily = float(np.sqrt(weights.T @ self.cov_matrix @ weights))
        volatility_annual = float(volatility_daily * np.sqrt(252))
        ratio = (
            expected_return_annual / volatility_annual if volatility_annual > 0 else np.nan
        )
        weights_series = pd.Series(weights, index=self.symbols)
        return PortfolioSolution(
            symbols=self.symbols,
            weights=weights_series,
            expected_return_daily=expected_return_daily,
            expected_return_annual=expected_return_annual,
            volatility_daily=volatility_daily,
            volatility_annual=volatility_annual,
            ratio=ratio,
        )


def risk_return_points(symbols: Sequence[str] | None = None) -> pd.DataFrame:
    stats = compute_descriptive_stats(symbols)
    return stats[
        [
            "Symbol",
            "Security Name",
            "mean_annual_return",
            "vol_annual",
            "return_risk_ratio",
        ]
    ]
