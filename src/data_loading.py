#   * lire tous les CSV,
#   * filtrer les tickers (liquidité, dates complètes),
#   * calculer les rendements journaliers,
#   * sortir un fichier propre `returns.parquet` ou `returns.csv`.
# * Un petit notebook “Exploration data / Nettoyage” avec :
#   * histogramme des volumes,
#   * exemple de série de prix.

from sys import stderr
import pandas as pd
import os

from paths import ROOT


meta = pd.read_csv(ROOT / "data/symbols_valid_meta.csv")

# Filtrage de base
meta = meta[
    (meta["Nasdaq Traded"] == "Y")
    & (meta["Test Issue"] == "N")
    & (meta["Financial Status"] == "N")
    & (meta["NextShares"] == "N")
]

# Calcul du volume total par symbole
records = []
for symbol in meta["Symbol"]:
    path = ROOT / f"data/stocks/{symbol}.csv"
    try:
        df = pd.read_csv(path, usecols=["Volume"])
        total_volume = df["Volume"].sum()
        records.append((symbol, total_volume))
    except Exception as e:
        print(f'error reading {path}', e, file=stderr)

volumes = pd.DataFrame(records, columns=["Symbol", "TotalVolume"])
meta = meta.merge(volumes, on="Symbol", how="left")

# Sélection 7 tickers par combinaison
groups = (
    meta.groupby(["Listing Exchange", "Market Category"])
    .apply(lambda g: g.nlargest(7, "TotalVolume"))
    .reset_index(drop=True)
)

groups.to_csv("selected_tickers.csv", index=False)
print(groups[["Listing Exchange", "Market Category", "Symbol", "TotalVolume"]])
