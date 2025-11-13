# Compte rendu de ce qui a été réalisé

## 1. Filtrage des tickers

On a plus de 8000 tickers. Pour simplifier les analyses, on a choisi une heuristique pour en sélectionner une
cinquantaine:

Déjà, on élimine:

- les tickers non NASDAQ (donc beaucoup de ListingExchange = N, A, P, Z)
- les tickers en difficulté financière (énorme dans les small caps)
- les ETF NextShares (assez rares mais ça retire aussi certains entrées)

Ensuite, on groupe chaque cours par couple (Listing Exchange, Market Ccategory) et on prend les N cours au volume total (somme de la colonne volume pour chaque jour de l'existence du cours) le plus élevé.

On a 7 groupes:

| Listing Exchange | Market Category | Count |
| ---------------- | --------------- | ----- |
| A                |                 | 253   |
| N                |                 | 2520  |
| P                |                 | 1542  |
| Q                | G               | 900   |
| Q                | Q               | 1531  |
| Q                | S               | 952   |
| Z                |                 | 351   |

On choisit N=7 ce qui nous donne 49 tickers dans notre dataset initial.

(Note: ça veut pas dire qu'on a 49 lignes. chaque ticker est associé à un fichier CSV avec une ligne par jour de l'existence du cours)

Voir [le schéma](./schema.md) pour la signification des lettres.
