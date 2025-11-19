# Projet d'analyse décisionnelle

Raphaël Bardini, Mattéo Pfranger, Valentin Conchis

## 1. Contexte & question de recherche

Un investisseur individuel souhaite constituer un petit portefeuille d'actions du NASDAQ (entre 3 et 10 titres), avec un objectif simple mais universel : obtenir un rendement intéressant sans exposer son capital à un risque excessif.

Il souhaite s'appuyer uniquement sur les données historiques avant la crise du Covid-19, considérée comme une période de marché « normal ».

> **Problématique :**
> *Comment choisir la répartition d'un portefeuille d'actions du NASDAQ pour maximiser le rendement espéré tout en maîtrisant le risque, à partir des données historiques jusqu'au 1ᵉʳ avril 2020 ?*

## 2. Choix du modèle

Nous avons choisi le modèle moyenne–variance de Harry Markowitz (1952), aussi appelé Modern Portfolio Theory.

### 2.1 Pourquoi ce modèle ?

* Pas de machine learning → modèle transparent, calculable et explicable
* Basé sur des outils statistiques classiques : moyenne, variance, covariance
* Permet de quantifier précisément le compromis rendement / risque
* Donne une décision optimisée, pas seulement une observation

### 2.2 Principe général

Pour chaque action, on calcule :

| Notion                         | Formule       | Interprétation                 |
| ------------------------------ | ------------- | ------------------------------ |
| Rendement moyen                | $\mu_i$     | Gain espéré                    |
| Risque (volatilité)            | $\sigma_i$  | Niveau de fluctuation          |
| Corrélation entre deux actions | $\rho_{ij}$ | Comment elles varient ensemble |

Ensuite, on ne regarde plus les actions séparément, mais le portefeuille comme une combinaison pondérée des actions :

$$
R_p = \sum_{i=1}^{n} w_i \mu_i
$$

$$
\sigma_p^2 = \sum_{i=1}^{n} \sum_{j=1}^{n} w_i w_j \sigma_i \sigma_j \rho_{ij}
$$

où :

* $w_i$ = poids du ticker dans le portefeuille
* $R_p$ = rendement espéré du portefeuille
* $\sigma_p$ = risque du portefeuille

### 2.3 Ce que permet le modèle

* Calculer le rendement espéré d'un portefeuille
* Calculer le risque total, y compris le risque dû à la corrélation entre les actions
* Trouver les poids optimaux pour un niveau de rendement souhaité
* Visualiser la Frontière efficiente, c'est-à-dire les meilleures combinaisons possibles rendement/risque

Ce modèle transforme littéralement une intuition ("plus de rendement = plus de risque") en équations et décisions concrètes.

## 3. Méthodologie et traitement des données

### 3.1 Source des données

Dataset : [Stock Market Dataset](https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset) (Kaggle)
*Cours quotidiens historiques des actions et ETFs du NASDAQ*

* CSV par ticker, répartis dans `stocks/` et `etfs/`
* `symbols_valid_meta.csv` contenant des métadonnées descriptives
* Période : selon les tickers, parfois depuis les années 60 → 1er avril 2020

### 3.2 Description des métadonnées

| Colonne              | Signification                                                                                                                                                                                  | Exemple                       | Utile pour l'analyse ?                                |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ----------------------------------------------------- |
| **Nasdaq Traded**    | Indique si le titre est coté sur le NASDAQ (`Y` = oui). Certains fichiers contiennent aussi des titres d'autres marchés (AMEX, NYSE).                                                          | `Y`                           | Oui, filtre de base (`Y` uniquement).                 |
| **Symbol**           | Code mnémonique du titre, le ticker.                                                                                                                                                           | `AAPL`, `MSFT`, `TSLA`        | Oui, c'est l'identifiant principal.                   |
| **Security Name**    | Nom complet de la société ou du fonds.                                                                                                                                                         | `"AAON, Inc. - Common Stock"` | Oui, utile pour visualisations et rapport.            |
| **Listing Exchange** | Code de l'exchange physique d'origine :  <br>• `Q` → NASDAQ <br>• `N` → NYSE <br>• `A` → AMEX                                                                                                  | `Q`                           | Filtre : garder `Q` pour rester sur le NASDAQ pur.    |
| **Market Category**  | Catégorie de marché NASDAQ :  <br>• `Q` = **Global Select Market** (grandes entreprises, les plus liquides) <br>• `G` = **Global Market** (mid-cap) <br>• `S` = **Capital Market** (small-cap) | `Q`, `G`, `S`                 | Oui, excellent critère pour équilibrer l'échantillon. |
| **ETF**              | Indique si c'est un Exchange-Traded Fund (`Y` = oui).                                                                                                                                          | `N`                           | Oui                                                   |
| **Round Lot Size**   | Nombre d'actions dans un lot standard (souvent 100). Sert aux traders institutionnels, pas utile ici.                                                                                          | `100.0`                       | Ignorable.                                            |
| **Test Issue**       | `Y` si c'est un titre de test (fictif).                                                                                                                                                        | `N`                           | À exclure (`N` uniquement).                           |
| **Financial Status** | État financier du titre :  <br>• `N` = normal <br>• `D` = en difficulté <br>• `E` = défaillant (delisting proche)                                                                              | `N`                           | Garder uniquement `N`.                                |
| **CQS Symbol**       | Code utilisé dans le *Consolidated Quote System* (souvent identique à `Symbol`).                                                                                                               | `AAON`                        | Redondant.                                            |
| **NASDAQ Symbol**    | Variante interne du ticker NASDAQ.                                                                                                                                                             | `AAON`                        | Redondant.                                            |
| **NextShares**       | `Y` si c'est un produit "NextShares” (fonds semi-actifs).                                                                                                                                      | `N`                           | Exclure (`N`).                                        |

### 3.3 Filtrage des tickers

Plus de 8000 tickers au départ.
On applique plusieurs filtres :

1. Exclure :
   * Titres non cotés au NASDAQ (`Nasdaq Traded ≠ Y`)
   * Titres de test (`Test Issue = Y`)
   * Titres en difficulté (`Financial Status ≠ N`)
   * Produits NextShares
2. Regrouper par couple (Listing Exchange, Market Category) :
   Chaque couple représente un pan du marché (taille, liquidité, réglementation).
3. Pour chaque groupe, sélectionner les 7 tickers ayant le volume total le plus élevé. Ce critère favorise les actions :
   * les plus liquides
   * les plus anciennes
   * avec un historique complet pour une analyse fiable

On obtient finalement 49 tickers, représentatifs et exploitables.

| Listing Exchange | Market Category | Nombre de tickers |
| ---------------- | --------------- | ----------------- |
| A                |                 | 253               |
| N                |                 | 2520              |
| P                |                 | 1542              |
| Q                | G               | 900               |
| Q                | Q               | 1531              |
| Q                | S               | 952               |
| Z                |                 | 351               |

## 4. Résultats et interprétation

Observations clés :

* Le rendement est généralement corrélé au risque (volatilité) : les titres très performants sont aussi les plus instables.
* Les portefeuilles diversifiés sont moins risqués que la simple moyenne du risque des actions : la corrélation entre actions permet d'atténuer le risque global.
* Un portefeuille avec des actions non corrélées (ou faiblement corrélées) est plus efficace qu'un portefeuille avec des actions très corrélées.
* La frontière efficiente montre clairement quelles combinaisons sont optimales, et lesquelles sont dominées.

## 5. Limites et pistes d'amélioration

### 5.1 Limites de notre application

Le tableau de bord actuel permet :

* d'analyser des tickers choisis par l'utilisateur
* de calculer un portefeuille optimisé
* de visualiser risque, rendement, corrélation, optimisation

Mais il ne permet pas encore :

* de proposer automatiquement le meilleur portefeuille parmi les 49 tickers
* de comparer plusieurs portefeuilles candidats
* d'intégrer plusieurs contraintes pratiques (frais, taxes, secteurs, ESG, etc.)

### 5.2 Limites du modèle de Markowitz

Le modèle repose sur des hypothèses très discutables dans la finance réelle :

| Hypothèse                                       | Limite réelle                                                      |
| ----------------------------------------------- | ------------------------------------------------------------------ |
| Les marchés sont objectivement mesurables       | Les prix réagissent à des facteurs irrationnels (peur, euphories&hellip;) |
| Les investisseurs sont rationnels               | Les émotions dominent souvent la prise de décision                 |
| Les rendements suivent une distribution normale | Les crises financières violent complètement cette hypothèse        |
| Les corrélations sont stables dans le temps     | En période de crise, toutes les actions chutent ensemble           |

Autrement dit : le modèle est très intéressant en période "normale”, mais il échoue souvent dans les situations extrêmes (crises de 2008, Covid, etc.).

## 6. Conclusion

Ce projet nous a permis :

* de manipuler un grand jeu de données boursières réelles
* d'appliquer un modèle statistique classique (mais puissant)
* de concevoir une interface interactive d'aide à la décision
* de comprendre que même les modèles mathématiques élégants&hellip; ont leurs limites dans le monde réel.
