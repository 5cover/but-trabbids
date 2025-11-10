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
