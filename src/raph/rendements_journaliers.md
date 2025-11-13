# Rendements journaliers

* **le quoi**,
* **le pourquoi**,
* **le comment**,
* **le code complet**,
  sans te noyer dans une forêt de `pandas.apply(lambda…)`.

Et oui, on parlera aussi de ce pauvre **Parquet**, qui n’est *pas* une branche tombée d’un chêne.

## 1. Le calcul du rendement journalier : ce que c’est

Tu as les prix ajustés quotidiennement (`Adj Close`).
Ton objectif : mesurer **l’évolution relative** d’un jour à l’autre.

**Formule standard :**

[
\text{return}*t = \frac{P_t - P*{t-1}}{P_{t-1}}
= \frac{P_t}{P_{t-1}} - 1
]

où (P_t) est le prix ajusté du jour t.

En pratique :

* si un titre passe de 100 → 103, le rendement = **3 %**
* si un titre passe de 50 → 49, le rendement = **-2 %**

Ce n’est pas un “prix”, c’est un **ratio** :
il permet de comparer des actifs très différents entre eux.

## 2. Pourquoi on calcule les rendements journaliers

Tu vas en avoir besoin partout :

### ✓ Pour les stats descriptives

* moyenne des rendements
* volatilité (écart-type)
* rendement annualisé (µ × 252)

### ✓ Pour la corrélation

Les prix ne sont pas stationnaires.
Les rendements le sont *à peu près*.
Donc corrélations = sur rendements, jamais sur prix.

### ✓ Pour la matrice de covariance

Ce sera l’entrée de ton modèle de portefeuille.

### ✓ Pour le portefeuille optimal

Ton modèle moyenne–variance repose **exclusivement sur les rendements**.

### ✓ Pour la simulation (test période COVID)

Tu peux appliquer ton portefeuille optimisé sur une série de rendements, pas une série de prix.

Bref, c’est LE carburant du projet.

## 3. Format de sortie : CSV VS Parquet

### CSV

* Texte lisible
* Facile à ouvrir dans Excel
* Lent à lire
* Prend beaucoup de place

### Parquet

* Format binaire **colonnaire**
* Ultra rapide à lire (10× plus vite)
* Ultra compact (compression automatique)
* Optimisé pour les pipelines data
* Pas en bois, désolé

Dans ton cas :
**Parquet est largement meilleur**.
Et tu peux charger un Parquet en Pandas d’un seul coup, sans parsing.

## 4. Structure du fichier final : `returns.parquet`

Format conseillé :

| date | symbol | return | adj_close |
| ---- | ------ | ------ | --------- |

Tu peux avoir une table longue (long format).
C’est parfait pour :

* faire un pivot,
* grouper par symbol,
* croiser symbol/date.

## 7. Notes importantes

### Sur les prix ajustés (“Adj Close”)

Toujours prendre ça, jamais “Close” :

* Adj Close corrige les **splits**
* et parfois les **dividendes**

Sans ça, tes rendements seraient faux.

### Sur la première valeur

La première ligne de chaque ticker n’a pas de rendement
(`pct_change()` donne NaN),
donc on la supprime.

### Sur les dates

Les dates sont des strings dans le CSV.
Tu pourras les convertir en datetime si besoin :

```python
df["Date"] = pd.to_datetime(df["Date"])
```

### Sur la fusion en un seul fichier

C’est volontaire.
Tu vas vouloir tout faire dessus :

* groupby symbol
* pivot table
* calculer la covariance

Donc autant tout mettre dans une seule table longue.

## 8. Résultat final

Tu obtiens un fichier `returns.parquet` contenant environ :

* 49 tickers
* 1500 à 4000 lignes chacun
* soit ~80k lignes

Parfait pour travailler rapidement sans recharger les CSV constamment.

## 9. Si tu veux aller plus loin

Je peux :

* te générer le script inverse (pivot pour obtenir un tableau Date × Symbol)
* t’aider à normaliser les dates
* t’aider à filtrer les périodes (pré-COVID/pendant-COVID)
* te fournir un mini notebook d’exploration

Dis-moi quand tu veux passer à la suite.
