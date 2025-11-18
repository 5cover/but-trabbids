# Plan de présentation (oral 10–12 min)

> Objectif : guider la démo live du dashboard Dash (`python -m src.dashboard.app`) et articuler le récit autour de la question décisionnelle.

## Slide 1 – Ouverture & Contexte *(0:00 – 0:45)*

- Titre du projet + logo NASDAQ.
- Problématique : **investisseur individuel** cherchant un portefeuille simple (≤10 titres) avant avril 2020.
- Rappeler brièvement la crise Covid qui arrive → besoin d’un portefeuille robuste.

## Slide 2 – Question décisionnelle *(0:45 – 1:20)*

- Formulation : *“Comment répartir 3 à 10 actions NASDAQ pour maximiser le rendement espéré en maîtrisant le risque (données jusqu’au 1ᵉʳ avril 2020) ?”*
- Critères de décision : rendement annualisé, volatilité, diversification.

## Slide 3 – Données & sélection de l’univers *(1:20 – 2:10)*

- Source Kaggle (Jackson Crow) : >8 000 tickers / 28 M lignes.
- Filtrage automatique (`python -m src.data_loading`) :
  - Nasdaq traded = Y, pas de “Test Issue”, pas de NextShares.
  - Top volumes par **Exchange × Market Category** → 49 tickers.
- Mention des métriques stockées (`selected_tickers.csv`), volumes moyens, période couverte.

## Slide 4 – Pipeline de préparation *(2:10 – 3:00)*

- Commande unique `python -m src.data_loading` :
  - Sélection (top volumes × Exchange/Category) → `selected_tickers.csv`.
  - Nettoyage prix 2010-01-04 → 2020-04-01 + clipping ±80 % → `prices.parquet`, `returns_(long|wide).parquet`.
  - Calcul des stats/corrélations → `stats_summary.(csv|parquet)`, `correlation_matrix.parquet`.
- Montrer schéma rapide (doc/schema.md) ou rappeler architecture `data/raw → data/processed → src`.

## Slide 5 – Statistiques descriptives *(3:00 – 4:00)*

- Focus sur les fichiers produits par le pipeline (μ/σ annualisés, volumes, rendement cumulatif).
- Exemple de résultats (AAPL, QQQ, TQQQ) avec ratio μ/σ > 1.
- Pointer l’importance de limiter la sélection à 5 tickers pour la lisibilité (prépare la démo).

## Slide 6 – Corrélations & dépendances *(4:00 – 4:45)*

- Heatmap corrélation pour détecter clusters (ETF tech, small caps…).
- Insight : combiner actifs faiblement corrélés (EXAS vs QQQ, etc.).
- Transition vers la modélisation moyenne–variance.

## Slide 7 – Modèle moyenne–variance *(4:45 – 5:45)*

- Rappeler notations : vecteur µ, matrice Σ, contraintes w ≥ 0, Σ w = 1, cap 35 % par actif.
- Outil : `src/analysis.py` + `cvxpy` (solveur Clarabel) → `MarkowitzModel`.
- Montrer formulation : min wᵀΣw s.t. wᵀµ ≥ µ* (optionnel).

## Slide 8 – Démo Dashboard : exploration *(5:45 – 7:15)*

- Lancer serveur (`python -m src.dashboard.app`).
- Parcours :
  1. Multi-dropdown → choisir 3 tickers (AAPL / QQQ / TQQQ).
  2. Basculer “Prix” / “Rendement cumulatif”.
  3. Lire tableau μ/σ, volumes.
  4. Montrer nuage risque/rendement + heatmap corrélation.

## Slide 9 – Démo Dashboard : optimisation *(7:15 – 9:00)*

- Section “Optimisation” :
  - Slider “Rendement annuel cible” (20 % par défaut).
  - Radio “Variance minimale” vs “Cible rendement”.
  - Bouton “Optimiser” → bar chart des poids, cartes KPI.
- Frontière efficiente + point optimisé.
- Backtest Jan–mars 2020 : comparatif portefeuille optimisé vs égalitaire vs QQQ.
- Mention limite 5 tickers pour garder solveur stable/lecture claire.

## Slide 10 – Recommandation & lecture des résultats *(9:00 – 10:00)*

- Exemple de portefeuille : 35 % AAPL, 35 % QQQ, 30 % EXAS (adapter selon démo).
- KPI clés : rendement annualisé attendu, volatilité, ratio μ/σ > 1.
- Souligner rôle de l’ETF QQQ comme socle + small cap pour booster le rendement.

## Slide 11 – Limites & pistes *(10:00 – 10:45)*

- Hypothèses : pas de frais, pas de ventes à découvert, historique limité pré-Covid.
- Sensibilité aux outliers (petits titres type PAE → cap poids ou filtrage futur).
- Améliorations possibles : scénarios post-Covid, contrainte sectorielle, Value-at-Risk.

## Slide 12 – Conclusion & Q/R *(10:45 – 11:30)*

- Résumer en 3 points :
  1. Pipeline reproductible + données propres.
  2. Dashboard interactif pour explorer rendement/risque.
  3. Modèle Markowitz interprétable pour la décision finale.
- Ouvrir sur les questions et prévoir un dernier retour au dashboard si besoin (ex: changer slider).
