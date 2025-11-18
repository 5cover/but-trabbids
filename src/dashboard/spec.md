# Fonctionnalités du tableau de bord Dash

*(spécification claire et exhaustive)*

## 1. Sélection de l’univers d’actions

### Composants

* Dropdown multi-sélection (`dcc.Dropdown`)
* Liste des **49 tickers**

### Fonctionnalité

* L’utilisateur peut sélectionner de **1 à 5 tickers** (pour éviter un graph illisible).
* La sélection déclenche la mise à jour :

  * du graphique des prix
  * des statistiques de rendements
  * du scatter risque/rendement

### Données affichées

* Nom du ticker
* Market Category
* Listing Exchange

## 2. Graphique des prix (vue temporelle)

### Visualisation

* `dcc.Graph` → **courbe des prix ajustés (Adj Close)**
* Option bascule “Prix” / “Rendement cumulatif” (`dcc.RadioItems`)

### Fonctionnalité

* Après sélection des tickers :

  * affichage de la courbe temporelle
  * couleurs distinctes pour chaque ticker
* Option “Normaliser à 100 au début” pour comparer facilement les trajectoires.

### Données utilisées

* Date
* Adj Close
* Rendement cumulatif = (Prix_t / Prix_0) × 100

## 3. Statistiques descriptives par ticker

### Visualisation

* Table (`dash_table.DataTable`) avec KPIs :

| KPI                    | Signification         |
| ---------------------- | --------------------- |
| μ annualisé            | Rendement moyen × 252 |
| σ annualisé            | Volatilité × √252     |
| Ratio rendement/risque | μ / σ                 |
| Volume moyen           | Liquidité             |
| Volume total           | Historique            |

### Fonctionnalité

* Se met à jour automatiquement selon les tickers choisis.
* Colonnes triables.

## 4. Matrice de corrélation

### Visualisation

* Heatmap `dcc.Graph` (plotly)

### Fonctionnalité

* Calculée sur les **rendements journaliers** des tickers sélectionnés.
* Color map centrée sur 0 (bleu → négatif, rouge → positif).
* Permet de repérer les corrélations fortes/faibles.

## 5. Nuage Risque vs Rendement (scatterplot)

### Visualisation

* `dcc.Graph` avec un point par ticker sélectionné :

  * X = σ annualisé
  * Y = μ annualisé

* Option d’afficher l'étiquette du ticker au survol.

### Fonctionnalité

* Permet de visualiser :

  * les actions “rentables mais risquées”
  * les actions “stables mais peu rentables”
  * les dominantes vs dominées
* Base indispensable pour introduire la frontière efficiente.

## 6. Optimisation du portefeuille (section centrale)

### Contrôles

* Slider `target_return` : rendement annuel visé (valeur dynamique)
* Bouton “Optimiser” (`dcc.Button`)
* Sélecteur :

  * “Portfolio minimal variance”
  * “Portfolio rendement-cible”

### Visualisations

* Graphique des poids (`dcc.Graph`):

  * Pie chart **ou** bar chart (bar chart recommandé, plus lisible)
* Tableau des résultats :

| Variable                            | Signification |
| ----------------------------------- | ------------- |
| Rendement du portefeuille optimisé  |               |
| Risque / Volatilité du portefeuille |               |
| Ratio rendement/risque              |               |
| Poids par action                    |               |

### Fonctionnalité

* Le slider modifie la contrainte ( w^T \mu ≥ R_{target} )
* Le bouton déclenche l’appel à `efficient_portfolio()`
* Poids recalculés en direct
* Les poids doivent :

  * être ≥ 0
  * sommer à 1

## 7. Courbe de la frontière efficiente

### Visualisation

* `dcc.Graph` :

  * X = risque
  * Y = rendement
  * Une courbe représentant les portefeuilles optimaux
  * Le point correspondant au portefeuille optimisé (slider) affiché en surbrillance

### Fonctionnalité

* Mode pré-calculé :

  * pour une grille de rendements cibles
  * évite de recalculer l’optimisation pour 100 points à chaque changement de ticker

### Données utilisées

* Rendements journaliers du sous-ensemble choisi
* Matrice de covariance
* Rendements moyens des tickers

## 8. Backtest du portefeuille (optionnel mais bonus)

### Visualisation

* Courbe du portefeuille optimisé sur les 3 derniers mois (jan–mars 2020)
* Comparaison avec :

  * un portefeuille égalitaire
  * un ticker référence (exemple : MSFT)

### Fonctionnalité

* Tester la robustesse du modèle en période de crise
* Mode “Test/Train” intégré dans un onglet secondaire

## 9. Infos générales / entête

### Visualisation

* Un bandeau avec :

  * Nombre de tickers sélectionnés
  * Période analysée
  * Source des données (NASDAQ)
  * Méthode de sélection (Exchange × Market Category × Volume total)

### Fonctionnalité

* Donner du contexte immédiatement au spectateur
* Faire pro dès la première seconde de présentation orale

## Résumé compact (à mettre dans vos slides)

## Le tableau de bord Dash permet :

### Exploration libre

* Sélectionner un sous-ensemble d’actions
* Visualiser prix et rendements cumulés
* Consulter KPIs (rendement, volatilité, ratio)

### Analyse statistique

* Matrice de corrélations
* Nuage risque/rendement
* Heatmap dynamique

### Décision & optimisation

* Choisir un rendement cible
* Calculer le portefeuille optimal
* Visualiser les poids
* Projeter le point optimal sur la frontière efficiente

### Bonus

* Backtest court sur la période Covid
* Interface prête à l’oral : slider + graphes + décision finale
