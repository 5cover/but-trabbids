import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA_PROCESSED = ROOT / 'data' / 'processed'

data = pd.read_csv(DATA_PROCESSED / "selected_tickers.csv")
returns = pd.read_parquet(DATA_PROCESSED / "returns.parquet")

# Garder uniquement les colonnes correspondant aux tickers sélectionnés
colonnes_communes = []
for symbol in data['Symbol'].unique():
    if symbol in returns.columns:
        colonnes_communes.append(symbol)
returns = returns[colonnes_communes]

# Nettoyage : supprimer lignes vides et valeurs aberrantes
# ----- ChatGPT -----
returns = returns.replace([np.inf, -np.inf], np.nan).dropna(how='all')
returns = returns.clip(lower=-1, upper=1)  # impossible d’avoir >100% ou <-100% par jour
# -------------------

# Calculs
rendements_moyens = returns.mean()
volatilites = returns.std()
rendements_annuels = ((1 + rendements_moyens) ** 252) - 1

# Rendement global
rendement_global_journalier = returns.stack().mean()
rendement_global_annuel = ((1 + rendement_global_journalier) ** 252) - 1

# ----- ChatGPT -----
print("Rendements par action :")
print(pd.DataFrame({
    'Moyenne': rendements_moyens,
    'Volatilité': volatilites,
    'Rendement annuel': rendements_annuels
}))
# -------------------

print(f"\nRendement global journalier moyen : {rendement_global_journalier:.6f}")
print(f"Rendement global annualisé : {rendement_global_annuel:.4%}")
