# Repository Guidelines

## Project Structure & Module Organization

`src/` contains every executable module: `data_loading.py` filters the Kaggle metadata, `raph/` turns raw prices into daily returns, `mato/` holds descriptive analytics, and `dashboard/` packages the Dash interface (`app.py`, design notes, shared paths). Keep raw downloads inside `data/raw/{stocks,etfs}`; scripts should only write curated artifacts to `data/processed/` (e.g., `selected_tickers.csv`, `returns.parquet`). Project notes stay in `doc/`, while experimental notebooks or quick utilities should live inside your module folder to avoid polluting the root.

## Build and Development Commands

```sh
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt
python src/data_loading.py                    # refresh selected tickers
python -m src.mato.stats_descriptives         # recompute KPIs
```

Run modules with `python -m …` so relative imports stay consistent with `src/paths.py`.

## Coding Style & Naming Conventions

Target Python 3.11+, four-space indentation, and PEP 8 naming (`snake_case` for functions, `PascalCase` for classes, screaming-case constants such as `DATA_PROCESSED`). Use `pathlib.Path` for IO and load configuration through `src/paths.py` rather than re-deriving roots. Dash work should separate layout and callbacks once multiple pages appear, and long-running steps belong behind `if __name__ == "__main__":` guards to keep imports light.

## Commit & Pull Request Guidelines

History shows short, lower-case French subjects (`ajout stats descriptive`, `cours`, `cr`). Keep using concise imperatives under 60 characters and group related edits together. Pull requests should include a tangible summary, reproduction steps (commands from above), expected outputs or screenshots for Dash changes, and references to doc updates or issues. Call out regenerated datasets so reviewers know when large files need to be recreated locally.

## Data & Security Notes

Never commit `data/raw/` contents or Kaggle keys; `.gitignore` already protects those directories, so verify with `git status` before pushing. When adding writers, emulate `src/paths.py` by ensuring target folders exist and by refusing to overwrite manually curated files without explicit confirmation.
