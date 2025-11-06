# Plan

## 1. Sujet & question décisionnelle

Contexte (à mettre tel quel dans le rapport, en mieux rédigé si tu veux) :

> Un investisseur individuel veut investir sur quelques actions du NASDAQ. Il veut un portefeuille simple (3 à 10 actions max) qui offre un bon compromis entre rendement et risque, en s’appuyant uniquement sur l’historique des cours avant la crise du Covid-19.

Question décisionnelle :

> “Comment choisir la répartition d’un portefeuille simple d’actions du NASDAQ pour maximiser le rendement espéré tout en maîtrisant le risque, à partir des données historiques jusqu’au 1er avril 2020 ?”

Modèle utilisé :
→ analyse descriptive + calcul des rendements + **modèle de portefeuille moyenne–variance (type Markowitz simplifié)**
Pas de ML, juste des maths classiques, super explicables.

## 2. Plan technique étape par étape (quoi / comment / pourquoi)

### Étape 0 – Organisation du projet (très rapide mais crucial)

Quoi

* Créer un repo Git (ou équivalent) avec une structure propre, par ex. :

  * `data/raw/` : les CSV téléchargés
  * `data/processed/` : dataset propre, aligné
  * `src/` : fonctions Python (`data_loading.py`, `model.py`, etc.)
  * `notebooks/` : notebooks d’analyse/visualisation
  * `reports/` : note explicative, slides

Comment

* Utiliser `pandas`, `numpy`, `matplotlib`/`seaborn`, éventuellement `scipy`.
* Décider ensemble du format final des données “propres” (DataFrame avec colonnes du type : `date`, `ticker`, `close`, `return`, etc.).

Pourquoi

* Si vous faites n’importe quoi là, vous allez souffrir plus tard. Et tu le sais.

### Étape 1 – Sélection de l’univers d’actions

Quoi

* Vous avez 8000 tickers. On ne va pas optimiser un portefeuille sur 8000 titres, vous n’êtes pas BlackRock.
* Restreindre à un sous-ensemble :

  * soit les X actions les plus liquides (volume moyen élevé),
  * soit un échantillon de 10–30 actions “représentatives” (tech, santé, industrie…).

Comment

* Charger `symbols_valid_meta.csv` pour lister les tickers.
* Calculer quelques indicateurs simples par ticker :

  * nombre de jours cotés,
  * volume moyen,
  * éventuellement prix moyen.
* Filtrer :

  * exclure les tickers avec trop de valeurs manquantes,
  * garder par ex. 20 actions avec forte liquidité.

Pourquoi

* Réduire la complexité,
* Rendre les visualisations lisibles,
* Avoir un univers stable sur plusieurs années.

### Étape 2 – Nettoyage et préparation des données

Quoi

* Mettre tous les tickers sélectionnés dans une **même structure tabulaire**.
* Calculer les **rendements journaliers** à partir du “Adj Close”.

Comment

1. Charger les CSV de chaque ticker sélectionné.
2. Vérifier (même si normalement c'est bon, mais ça ne fait rien de mal):
   * dates manquantes,
   * doublons,
   * valeurs aberrantes (prix à 0, volume 0 sur des jours bizarres).
3. Aligner les dates :
   * intersection des dates communes (tous les titres cotés ce jour),
   * ou bien autoriser des NaN mais ils seront gérés/filtrés ensuite.
4. Calculer `return_t = (AdjClose_t / AdjClose_{t-1}) - 1` pour chaque titre.
5. Sauvegarder un dataset propre, par ex. dans `data/processed/returns.parquet`.

Pourquoi

* Les modèles se basent sur les rendements, pas sur les prix bruts.
* Le prof attend explicitement : “Vérifier la qualité des données, valeurs manquantes, incohérences…”.

### Étape 3 – Analyse descriptive & KPIs de base

Quoi

* Faire des stats descriptives simples :

  * moyenne des rendements,
  * volatilité (écart-type),
  * rendement annualisé,
  * corrélation entre actions.

Comment

* Pour chaque ticker :

  * moyenne des rendements journaliers µ,
  * écart-type σ,
  * rendement annualisé ≈ µ × 252,
  * risque annualisé ≈ σ × √252.
* Matrice de corrélation des rendements journaliers.
* Visualisations :

  * courbe de prix de quelques actions sur 2015–2020,
  * histogrammes de rendements,
  * heatmap de corrélations.

Pourquoi

* Justifier les choix de titres (rendre le dataset intelligible),
* Introduire les notions de rendement / risque que vous utilisez ensuite dans le modèle.

### Étape 4 – Modèle décisionnel : portefeuille moyenne–variance

Quoi

* Construire un **modèle de portefeuille** :

  * Variables : les poids ( w_i ) de chaque action.
  * Contraintes :

    * ( w_i \ge 0 ) (pas de vente à découvert),
    * ( \sum_i w_i = 1 ).
  * Objectifs possibles :

    * Minimiser la variance pour un niveau de rendement cible,
    * ou maximiser un ratio type “rendement / risque”.

Comment (version “propre mais simple”)

1. Calculer :

   * vecteur des rendements espérés ( \mu ) (annualisé),
   * matrice de covariance ( \Sigma ) (annualisée).
2. Choisir un niveau de rendement cible ( R_{target} ).
3. Résoudre :

   * Minimise ( w^T \Sigma w )
   * sous contraintes ( w^T \mu \ge R_{target} ), ( w_i \ge 0 ), ( \sum w_i = 1 ).
4. Implémentation :

   * soit avec une bibliothèque de résolution (ex. `scipy.optimize.minimize`),
   * soit en version pédagogique avec un grid search simple si vous limitez à 2–3 actions (plus facile à expliquer oralement).

Visualisations à produire

* Nuage de points “Risque vs Rendement” pour chaque action prise individuellement.
* Courbe de la **frontière efficiente** (ensemble de portefeuilles optimaux).
* Comparaison de quelques portefeuilles spécifiques :

  * portefeuille égalitaire,
  * portefeuille optimisé pour faible risque,
  * portefeuille optimisé pour rendement.

Pourquoi

* Ça colle parfaitement à “optimisation, allocation de ressources”.
* Le modèle est mathématiquement classique, bien documenté, simple à expliquer.
* La décision finale est claire : “voici les poids recommandés”.

### Étape 5 – Validation / scénario de crise

Quoi

* Tester si votre portefeuille optimisé “tient le choc” face à la crise Covid (début 2020).

Comment

* Séparer la période en :

  * **période de calibration** : par ex. 2015–fin 2019,
  * **période de test** : janvier–1er avril 2020.
* Optimiser le portefeuille sur la période de calibration.
* Calculer :

  * performance cumulée du portefeuille sur la période de test,
  * comparer avec :

    * un portefeuille égalitaire,
    * une ou deux actions prises individuellement.

Pourquoi

* Ça donne un argument réaliste : “notre modèle marche dans un environnement normal, mais il montre ses limites en crise extrême”.
* Point bonus pour l’esprit critique dans la présentation.

### Étape 6 – Interface / tableau de bord simple

Quoi

* Un petit truc interactif (ou pseudo-interactif) pour cocher la case “visualisation / test de valeurs”.

Comment

* Dans un notebook :

  * une cellule où on change un rendement cible et on recalcul le portefeuille,
  * ou un slider avec `ipywidgets` pour ajuster ( R_{target} ) et afficher les poids.
* Ou alors un script Python qui prend en entrée un rendement cible et affiche :

  * les poids par action,
  * les indicateurs (rendement / risque du portefeuille).

Pourquoi

* C’est exactement ce que le prof demande : “tester une valeur aléatoire ou une simulation”.
* Ça donne un effet “outil décisionnel” et pas juste “TP de stats”.

## 3. Livrables

Code source

* Scripts Python bien découpés :

  * `data_loading.py` : chargement, nettoyage.
  * `features.py` : calcul des rendements, stats descriptives.
  * `portfolio_model.py` : calcul de µ, Σ, optimisation.
  * `visuals.py` : graphiques de base.
* Un notebook principal `notebooks/rapport.ipynb` qui raconte toute l’histoire.

Note explicative (2–4 pages)
Plan possible :

1. Contexte & question

   * Marché boursier, NASDAQ, investisseur fictif.
   * Formulation de la question décisionnelle.

2. Données & préparation

   * Description du dataset.
   * Filtrage des actions, période étudiée.
   * Nettoyage, création des rendements.

3. Modèle décisionnel

   * Définition du rendement espéré, du risque (variance).
   * Présentation du modèle moyenne–variance.
   * Explication des contraintes.

4. Résultats

   * Stats descriptives (tableau, graphiques).
   * Frontière efficiente, portefeuilles testés.
   * Résultats en période normale vs période de crise.

5. Interprétation, limites, améliorations

   * Recommandation de portefeuille.
   * Limites (hypothèses fortes, pas de prise en compte des frais, comportements extrêmes).
   * Ce qu’un modèle plus avancé pourrait ajouter (mais hors scope du projet).

Présentation orale (10–15 min)

* 1 slide contexte & question.
* 2–3 slides données & nettoyage.
* 3–4 slides sur le modèle, les formules, la frontière efficiente.
* 2–3 slides résultats + scénario crise.
* 1 slide limites & décision finale.

## 4. Répartition des tâches (travail en parallèle)

Je te propose un découpage qui limite les blocages entre vous trois.

### Raphaël – Data & préparation (le gardien du dataset)

Responsable de :

* Étape 1 & 2 principalement.
* Scripts pour :

  * lire tous les CSV,
  * filtrer les tickers (liquidité, dates complètes),
  * calculer les rendements journaliers,
  * sortir un fichier propre `returns.parquet` ou `returns.csv`.
* Un petit notebook “Exploration data / Nettoyage” avec :

  * histogramme des volumes,
  * exemple de série de prix.

Pourquoi lui

* Son boulot peut être fait en parallèle, et une fois qu’il a figé le format “officiel” des données, les deux autres peuvent l’utiliser sans attendre.

### Mattéo – Modélisation & maths (le maso volontaire)

Responsable de :

* Étape 3 & 4 principalement.
* À partir du fichier propre de Raphaël :

  * calcul des rendements moyens, variances, covariances,
  * calcul des indicateurs annualisés,
  * implémentation du modèle de portefeuille :

    * fonction `optimize_portfolio(target_return)` ou équivalent,
    * frontiere efficiente.
* Explication mathématique dans le rapport :

  * définition de µ, Σ,
  * expression de la variance de portefeuille,
  * formulation du problème d’optimisation.

Pourquoi lui

* Son travail dépend surtout du format de données, mais il peut déjà coder et tester avec un dataset factice (ex. 3–4 actions) avant même que Raphaël ait fini.

### Valentin – Visualisation & storytelling (la surface humaine du projet)

Responsable de :

* Étape 3 (viz), 5 & 6, plus grosse partie de la note et des slides.
* Graphiques :

  * prix dans le temps,
  * histogrammes des rendements,
  * nuage de points “risque vs rendement”,
  * visualisation de la frontière efficiente.
* Notebooks / interface :

  * notebook final qui enchaîne les étapes dans l’ordre,
  * éventuellement widgets pour changer un rendement cible.
* Rapport écrit :

  * mise en forme du contexte, interprétation des résultats, limites.
* Slides de présentation, en structurant les sections de chacun.

Pourquoi lui

* Il dépend des fonctions de Mattéo et des données de Raphaël, mais :

  * il peut travailler sur la structure du rapport et des slides dès le début,
  * il peut commencer avec des graphiques de test sur un sous-ensemble fourni rapidement.

## 5. Synchronisation entre vous

Pour éviter l’effet “tout le monde attend tout le monde” :

* Dès le début, vous fixez ensemble :

  * le format de la table finale (colonnes, types),
  * le nom des fonctions “publiques” (ex. `load_returns()`, `optimize_portfolio()`).
* Raphaël peut livrer rapidement une **version minimale** du dataset (ex. 5 tickers sur 2 ans) pour que Mattéo et Valentin puissent développer.
* Ensuite, il l’étend à l’univers final (20 tickers, 2015–2020) sans casser l’API.

Comme ça, chacun peut travailler en parallèle sans passer sa vie à se ping sur “t’as fini ton CSV ?”.

Si vous faites ça proprement, votre prof risque de vous prendre pour des gens organisés et rationnels. Je sais, c’est perturbant.
