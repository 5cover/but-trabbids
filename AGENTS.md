# Repository Guidelines

## Project Structure & Module Organization

`src/` contient les modules exécutables. `data_loading.py` pilote désormais tout le pipeline (sélection des tickers, historique prix/rendements, stats). `dashboard/` regroupe l’app Dash (`app.py`, design notes, shared paths). Gardez les téléchargements bruts dans `data/raw/{stocks,etfs}` ; les scripts doivent uniquement écrire les artefacts nettoyés dans `data/processed/` (`selected_tickers.csv`, `prices.parquet`, etc.). Les notes vont dans `doc/`, et les utilitaires temporaires restent dans votre sous-module pour préserver la racine.

## Build and Development Commands

```sh
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt
python -m src.data_loading                  # pipeline complet (sélection + rendements + stats)
```

Run modules with `python -m …` so relative imports stay consistent with `src/paths.py`.

## Coding Style & Naming Conventions

Target Python 3.11+, four-space indentation, and PEP 8 naming (`snake_case` for functions, `PascalCase` for classes, screaming-case constants such as `DATA_PROCESSED`). Use `pathlib.Path` for IO and load configuration through `src/paths.py` rather than re-deriving roots. Dash work should separate layout and callbacks once multiple pages appear, and long-running steps belong behind `if __name__ == "__main__":` guards to keep imports light.

## Commit & Pull Request Guidelines

History shows short, lower-case French subjects (`ajout stats descriptive`, `cours`, `cr`). Keep using concise imperatives under 60 characters and group related edits together. Pull requests should include a tangible summary, reproduction steps (commands from above), expected outputs or screenshots for Dash changes, and references to doc updates or issues. Call out regenerated datasets so reviewers know when large files need to be recreated locally.

## Data & Security Notes

Never commit `data/raw/` contents or Kaggle keys; `.gitignore` already protects those directories, so verify with `git status` before pushing. When adding writers, emulate `src/paths.py` by ensuring target folders exist and by refusing to overwrite manually curated files without explicit confirmation.
