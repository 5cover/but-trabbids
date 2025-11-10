#   * lire tous les CSV,
#   * filtrer les tickers (liquidité, dates complètes),
#   * calculer les rendements journaliers,
#   * sortir un fichier propre `returns.parquet` ou `returns.csv`.
# * Un petit notebook “Exploration data / Nettoyage” avec :
#   * histogramme des volumes,
#   * exemple de série de prix.

from csv import DictReader
from pathlib import Path
import pandas as pd

from paths import ROOT
from paths import DATA_PROCESSED, DATA_RAW

N = 7

meta = pd.read_csv(DATA_RAW / "symbols_valid_meta.csv")

# Filtrage de base
meta = meta[
    (meta["Nasdaq Traded"] == "Y")
    & (meta["Test Issue"] == "N")
    & (meta["Financial Status"] == "N")
    & (meta["NextShares"] == "N")
]

def sum_volume_fast(path: Path):
    try:
        with open(path, newline="") as f:
            reader = DictReader(f)
            return sum(int(row["Volume"]) for row in reader if row["Volume"])
    except Exception:
        return None

# Calcul du volume total par symbole
records = []
for symbol, is_etf in meta[["Symbol", "ETF"]].values:
    path = DATA_RAW / ('etfs' if is_etf == "Y" else 'stocks') / f'{symbol}.csv'
    print('Processing', symbol)
    df = pd.read_csv(path, usecols=["Volume"])
    total_volume = df["Volume"].sum()
    records.append((symbol, total_volume))

volumes = pd.DataFrame(records, columns=["Symbol", "TotalVolume"])
meta = meta.merge(volumes, on="Symbol", how="left")

# Sélection N tickers par combinaison
groups = (
    meta.groupby(["Listing Exchange", "Market Category"], dropna=False)
    .apply(lambda g: g.nlargest(N, "TotalVolume"))
    .reset_index(drop=True)
)

groups.to_csv(DATA_PROCESSED / "selected_tickers.csv", index=False)
print(groups[["Listing Exchange", "Market Category", "Symbol", "TotalVolume"]])
