# Trabbids

Analyse de données financières pour aide au trading semi-automatisé

&copy; Mattéo Pfranger, Valentin Conchis, Raphaël Bardini &ndash; 2025

## Running

```sh
./run.sh
```

## Installation

Perform these steps once to run the application.

### 0. Clone repository

You probably know how to do this, but here is a reminder

```sh
git clone https://github.com/5cover/but-trabbids.git
cd but-trabbids
```

### 1. Download & unzip dataset

- Download dataset from [Dataset](https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset) as file "archive.zip" in the project root

```sh
mkdir -p data
unzip archive.zip -d data/raw
```

### 2. Install dependencies

```sh
# in project root
python3 -m venv venv # py on windows
. venv/bin/activate # or venv/Scripts on windows
pip install -r requirements.txt
pip install -e .
```

## Satistiques

Nombre total de lignes: 28167857

Calculé avec `find data/raw -type f -print0 | wc --files0-from=- -l`
