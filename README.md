# Trabbids

Analyse de données financières pour aide au trading semi-automatisé

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
