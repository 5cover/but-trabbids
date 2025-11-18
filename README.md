# Trabbids

Analyse de données financières pour aide au trading semi-automatisé

&copy; Mattéo Pfranger, Valentin Conchis, Raphaël Bardini &ndash; 2025

## Setup rapide

```sh
# in project root
python3 -m venv venv # Créer un environnement virtuel
. venv/bin/activate # Activer l'environnement
pip install -r requirements.txt
```

## Satistiques

Nombre total de lignes: 28167857

Calculé avec `find data/raw -type f -print0 | wc --files0-from=- -l`

## Liens

[Dataset](https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset)

Extraction steps:

1. Download archive to the root directory of the project
2. Unzip the archive to the /dataset directory:

  ```sh
  mkdir -p data
  unzip archive.zip -d data/raw
  ```

## Results

• Implementation Summary

- Rewrote the ticker selection CLI to ingest Nasdaq metadata, infer filenames safely, compute per-symbol liquidity stats, and emit a clean 49-ticker
    universe ready for scripting; configurable args let you tweak date cutoffs and bucket sizes whenever you refresh (src/data_loading.py:1).
- The returns builder now enforces the 2010‑2020 window, clips absurd pct changes, normalizes prices, and writes both long/pivot parquet datasets so
    every module (stats, dashboard, optimizer) can reuse the same curated artifacts (src/raph/rendements_journaliers.py:1).
- Introduced a shared analytics toolkit with cached loaders, descriptive KPI computation, correlation helpers, and a Markowitz optimizer that caps
    single-asset exposure while supporting target-return or min-variance modes; the stats CLI simply exports summary/correlation tables from those
    primitives (src/analysis.py:19, src/mato/stats_descriptives.py:1).
- Built the full Dash experience: multi-select universe controls, KPI table, risk/rend charts, correlation heatmap, optimization controls, weight bars,
    frontier plot, and a Jan–Mar 2020 backtest, all styled via a lightweight CSS theme for the oral demo (src/dashboard/app.py:1, src/dashboard/assets/
    style.css:1).
- Added the missing solver dependency so cvxpy/Clarabel is available for both the CLI model and the dashboard (requirements.txt:7).
- Documented the oral flow with a slide-by-slide playbook that ties the story to the live dashboard checkpoints (presentation_plan.md:1).

  Tests

- python -m src.data_loading --max-symbols 49
- python -m src.raph.rendements_journaliers
- python -m src.mato.stats_descriptives
- Smoke test: python -m src.dashboard.app (launched then terminated after verifying startup)

  Next Steps

  1. Before the oral, launch python -m src.dashboard.app once to warm caches and confirm data loads quickly.
  2. If you want to keep the optimizer from suggesting exotic tickers (e.g. PAE), consider filtering them out via --symbols on stats_descriptives or by
     raising min_trading_days in src.data_loading.
