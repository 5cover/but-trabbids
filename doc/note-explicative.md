# Trabbids - Understanding Stock Market Patterns

(not related to rabbids)

## 1 Contexte & question de recherche

Un investisseur individuel veut investir sur quelques actions du NASDAQ. Il veut un portefeuille simple (3 à 10 actions max) qui offre un bon compromis entre rendement et risque, en s’appuyant uniquement sur l’historique des cours avant la crise du Covid-19.

Comment choisir la répartition d’un portefeuille simple d’actions du NASDAQ pour maximiser le rendement espéré tout en maîtrisant le risque, à partir des données historiques jusqu’au 1er avril 2020 ?

## 2 Choix du modèle

- analyse descriptive
- calcul des rendements
- modèle de portefeuille moyenne–variance (type Markowitz simplifié)

Pourquoi:

- Pas de ML
- Explicable et interprétable
- Performant à calculer

Donc:

- analyse purement statistique
- évaluation et optimisation de positions boursières
- le trader garde la main. le programme informe.

## 3 Méthodologie et traitement des données

### 3.1 Dataset

[Stock Market Dataset](https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset)

*Historical daily prices of Nasdaq-traded stocks and ETFs*

Source: `nasdaqtrader.comer` Yahoo Finance

Plage temporelle : années 60 (selon les date de naissance des cours) au 1er avril 2020.

Contenu:

1. CSVs par ticker dans sous dossiers `stocks` ou `etfs` selon
2. Un `symbols_valid_meta`.csv avec des les métadonnées pour chaque ticker.

### 3.2 schéma


| Colonne              | Signification                                                                                                                                                                                  | Exemple                       | Utile pour l'analyse ?                                |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ----------------------------------------------------- |
| **Nasdaq Traded**    | Indique si le titre est coté sur le NASDAQ (`Y` = oui). Certains fichiers contiennent aussi des titres d’autres marchés (AMEX, NYSE).                                                          | `Y`                           | Oui, filtre de base (`Y` uniquement).                 |
| **Symbol**           | Code mnémonique du titre, le ticker.                                                                                                                                                           | `AAPL`, `MSFT`, `TSLA`        | Oui, c’est l’identifiant principal.                   |
| **Security Name**    | Nom complet de la société ou du fonds.                                                                                                                                                         | `"AAON, Inc. - Common Stock"` | Oui, utile pour visualisations et rapport.            |
| **Listing Exchange** | Code de l’exchange physique d’origine :  <br>• `Q` → NASDAQ <br>• `N` → NYSE <br>• `A` → AMEX                                                                                                  | `Q`                           | Filtre : garder `Q` pour rester sur le NASDAQ pur.    |
| **Market Category**  | Catégorie de marché NASDAQ :  <br>• `Q` = **Global Select Market** (grandes entreprises, les plus liquides) <br>• `G` = **Global Market** (mid-cap) <br>• `S` = **Capital Market** (small-cap) | `Q`, `G`, `S`                 | Oui, excellent critère pour équilibrer l'échantillon. |
| **ETF**              | Indique si c’est un Exchange-Traded Fund (`Y` = oui).                                                                                                                                          | `N`                           | Oui                                                   |
| **Round Lot Size**   | Nombre d’actions dans un lot standard (souvent 100). Sert aux traders institutionnels, pas utile ici.                                                                                          | `100.0`                       | Ignorable.                                            |
| **Test Issue**       | `Y` si c’est un titre de test (fictif).                                                                                                                                                        | `N`                           | À exclure (`N` uniquement).                           |
| **Financial Status** | État financier du titre :  <br>• `N` = normal <br>• `D` = en difficulté <br>• `E` = défaillant (delisting proche)                                                                              | `N`                           | Garder uniquement `N`.                                |
| **CQS Symbol**       | Code utilisé dans le *Consolidated Quote System* (souvent identique à `Symbol`).                                                                                                               | `AAON`                        | Redondant.                                            |
| **NASDAQ Symbol**    | Variante interne du ticker NASDAQ.                                                                                                                                                             | `AAON`                        | Redondant.                                            |
| **NextShares**       | `Y` si c’est un produit “NextShares” (fonds semi-actifs).                                                                                                                                      | `N`                           | Exclure (`N`).                                        |

### 3.3 Filtrage des tickers

On a plus de 8000 tickers. Pour simplifier les analyses, on a choisi une heuristique pour en sélectionner une
cinquantaine:

Déjà, on élimine:

- les tickers non NASDAQ (donc beaucoup de ListingExchange = N, A, P, Z)
- les tickers en difficulté financière (énorme dans les small caps)
- les ETF NextShares (assez rares mais ça retire aussi certains entrées)

Ensuite, on groupe chaque cours par couple (Listing Exchange, Market Category) et on prend les N cours au volume total (somme de la colonne volume pour chaque jour de l'existence du cours) le plus élevé.

On a 7 groupes:

| Listing Exchange | Market Category | Nombre de tickers |
| ---------------- | --------------- | ----------------- |
| A                |                 | 253               |
| N                |                 | 2520              |
| P                |                 | 1542              |
| Q                | G               | 900               |
| Q                | Q               | 1531              |
| Q                | S               | 952               |
| Z                |                 | 351               |

On choisit $N=7$ ce qui nous donne 49 tickers dans notre dataset initial.

(Note: ça veut pas dire qu'on a 49 lignes. chaque ticker est associé à un fichier CSV avec une ligne par jour de l'existence du cours)

### 3.4 Par rapport au couples (Listing Exchange, Market Category)

Chacune représente un pan distinct du marché : capitalisation, liquidité et réglementation.

Pour chaque combinaison, nous avons retenu les 7 titres au volume total cumulé le plus élevé sur toute la période disponible (jusqu’au 1ᵉʳ avril 2020).
Ce choix privilégie les titres ayant un historique complet et une forte liquidité, assurant une meilleure comparabilité et une série temporelle plus longue pour l’analyse statistique.

## 4 Résultats et interprétation

TBD

## 5 Limites et pistes d'amélioration

TBD
