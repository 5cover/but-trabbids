# Guide fonctionnel – Analyse & Tableau de bord NASDAQ (pré‑Covid)

Ce document sert de porte d’entrée pour toute personne qui rejoint le projet en dernière minute. Il retrace le pipeline d’analyse, résume les indicateurs que nous calculons et explique comment lire le tableau de bord Dash même si vous avez peu de notions financières.

## 1. Vue d’ensemble du pipeline

| Étape                        | Script                                      | Pourquoi ?                                                                                                   | Fichiers produits                                                |
| ---------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Sélection des tickers        | `python -m src.data_loading`                | Choisir un univers réduit mais liquide via les métadonnées Nasdaq (volumes, catégorie de marché, ETF ou non) | `data/processed/selected_tickers.csv`                            |
| Historique prix & rendements | `python -m src.raph.rendements_journaliers` | Aligner les séries 2010‑01‑04 → 2020‑04‑01, nettoyer les prix et calculer les rendements journaliers         | `prices.parquet`, `returns_long.parquet`, `returns_wide.parquet` |
| Statistiques descriptives    | `python -m src.mato.stats_descriptives`     | Calculer les KPI par titre (rendement, risque, volumes) + matrice de corrélation                             | `stats_summary.(csv                                              | parquet)`,`correlation_matrix.parquet` |
| Modèle de portefeuille       | `src/analysis.py` (importé par la Dash app) | Implémenter le modèle moyenne–variance de Markowitz avec contraintes simples (poids ≥ 0, ≤ 35 %)             | Objets Python (pas de fichier)                                   |
| Tableau de bord              | `python -m src.dashboard.app`               | Montrer visuellement prix, stats, corrélations et optimisation en direct pendant l’oral                      | Serveur Dash (port 8050)                                         |

> **Astuce onboarding** : si un fichier manque, relancez simplement les modules ci-dessus dans l’ordre. Ils s’appuient tous sur `src/paths.py`, donc exécutez-les depuis la racine du projet.

## 2. Comprendre les métriques clés

### Rendement moyen (µ)

- **Journalier** : moyenne des variations `%` jour après jour.
- **Annualisé** : `(1 + µ_jour)^252 – 1` (252 ~ nombre de séances boursières/an).
- L’idée : plus µ est élevé, plus l’actif “rapporte” sur le long terme, mais ce n’est qu’un indicateur historique.

### Volatilité (σ)

- Mesure la dispersion des rendements journaliers (écart-type).
- Annualisée via `σ_jour × √252`.
- Interprétation simple : plus σ est gros, plus la courbe de prix “bouge” → risque plus élevé.

### Ratio µ/σ

- Rendement espéré par unité de risque (proche de l’idée du Sharpe sans taux sans risque).
- >1 signifie “rendement historique supérieur à la volatilité”, donc attrayant dans ce cadre simplifié.

### Corrélation

- Valeurs entre ‑1 et +1.
- 1 → deux titres évoluent quasi pareil (peu de diversification).
- 0 → mouvements indépendants.
- ‑1 → évolutions opposées (rare mais idéal pour lisser la volatilité).

### Poids du portefeuille

- Contraintes : somme = 1 (100 % du capital), poids ≥ 0 (pas de ventes à découvert), cap de 35 % (configurable) par titre pour éviter la concentration.
- Calculés par `cvxpy` en minimisant la variance ou en atteignant un rendement cible.

## 3. Ce que montre le Dashboard et comment le lire

### 3.1 Sélection et bandeau d’information

- **Multi-dropdown** limité à 5 tickers : on privilégie la lisibilité et la stabilité du solveur.
- **Bandeau contexte** : rappelle combien de titres sont sélectionnés, la période couverte (2010‑01‑04 → 2020‑04‑01) et la méthode de filtrage (volumes × catégorie).
- **Alerte** : si vous dépassez la limite ou qu’un titre n’existe plus dans les données, un message apparaît sous les contrôles.

### 3.2 Graphique de prix / rendement cumulatif

- **Basculer “Prix” ↔ “Rendement cumulatif”** :  
  - *Prix* montre les dollars “Adj Close”.  
  - *Rendement cumulatif* normalise toutes les courbes à 100 le 1ᵉʳ jour → parfait pour comparer trajectoires.
- En un clin d’œil : repérez les titres plus résilients (courbes moins chahutées) vs ceux qui explosent avant 2020 (ETF levier type TQQQ).

### 3.3 Tableau de KPIs

- Colonnes déjà formatées (pourcentages, volumes groupés) pour repérer :
  - µ annualisé : rendement historique.
  - σ annualisé : risque.
  - µ/σ : “bang for the buck”.
  - Volume moyen/total : liquidité → un titre très peu échangé est risqué (difficile à vendre en crise).
- Triez en cliquant sur les en-têtes pour identifier rapidement les meilleurs ratios ou les titres les plus liquides.

### 3.4 Nuage Risque vs Rendement

- Chaque point = un titre sélectionné.
- Axe X = σ (risque), axe Y = µ (rendement).
- Idées à verbaliser :
  - Points en haut/gauche : combinaison rare (rendement élevé pour risque modéré).
  - Points très à droite : titres volatils (ex : TQQQ).
  - Points dominés : si un autre titre fait mieux sur les deux axes, inutile de le garder.
- Taille des points : proportionnelle au ratio µ/σ mais toujours positive (on clippe les ratios négatifs et on ajoute un mini-offset). Un gros disque = titre historiquement “efficace” (µ élevé relativement à son risque). Un disque minuscule = ratio ≤ 0 → le titre n’a pas compensé sa volatilité, à mentionner pendant l’oral.

### 3.5 Matrice de corrélation

- Heatmap rouge = corrélation positive forte, bleu = corrélation négative.
- Objectif pédagogique : montrer que mixer des secteurs/produits faiblement corrélés réduit la volatilité globale.
- Survolez pour lire la valeur exacte; écarter les paires >0.9 si l’on veut diversifier.

### 3.6 Contrôles d’optimisation

- **Mode portefeuille** :
  - *Variance minimale* : minimise le risque sans contrainte de rendement.
  - *Cible rendement* : impose un µ annualisé (slider) puis trouve la variance minimale possible.
- **Slider rendement** : fixé par défaut à 20 % annuel, mais vous pouvez tester 30 %, 40 % pour montrer l’impact sur les poids. Il se grise automatiquement si vous passez en mode “Variance minimale” (puisqu’il n’est pas utilisé).
- **Poids max par titre** : slider dédié (20 % → 100 %). 35 % par défaut = “pas plus d’un tiers du capital sur un seul actif”. Abaisser ce cap force la diversification, l’augmenter montre ce qui se passe avec un portefeuille plus concentré.
- **Bouton “Optimiser”** : force le recalcul (utile pendant l’oral pour rythmer le discours).

### 3.7 Résultats de l’optimisation

- **Bar chart des poids** : lisible instantanément (valeurs arrondies en %).  
  - Le titre du graphique rappelle le cap choisi (ex : “cap 35 %”). Si une barre touche cette limite, c’est que le solveur la “pousse” au maximum autorisé.
- **Cartes KPI** :  
  - Rendement annualisé attendu du portefeuille.
  - Volatilité annualisée (le “risque global”).
  - Ratio µ/σ du portefeuille.
- **Frontière efficiente** :
  - Ligne bleue = série de portefeuilles calculés sur une grille de rendements cibles (par ex. 10 %, 20 %, …). Chaque point représente la variance minimale atteignable sous le cap de poids choisi.
  - Points gris = titres individuels (volatilité vs rendement) → utile pour rappeler que certains titres sont “dominé” même avant optimisation.
  - Point orange = portefeuille optimisé courant (soit variance min, soit cible). Pendant l’oral, insistez sur la comparaison : “notre portefeuille (orange) offre X % de rendement pour Y % de risque, mieux que n’importe quel titre pris isolément”.
- **Backtest Jan–Mars 2020** :
  - Courbes base 100 comparant trois stratégies : (1) portefeuille optimisé (poids calculés), (2) portefeuille égalitaire (chaque ticker = 1/n), (3) benchmark historique (QQQ ou premier ticker si QQQ absent).
  - Lecture : regardez les écarts pendant la mini-crise de mars 2020. Si la courbe optimisée chute moins ou remonte plus vite que l’égalitaire, cela valide la diversification / objectif choisi. Si elle fait pire, soulignez les limites (modèle calibré sur tout 2010‑2020, pas spécifiquement sur la crise).
- **Message “Optimisation impossible: Optimisation échouée (infeasible).”** :
  - Pourquoi ? Les contraintes n’ont pas de solution (ex : un seul ticker sélectionné avec limite 35 %, ou un rendement cible irréaliste de 80 % sur des titres prudents). Le solveur Clarabel signale alors que le problème est “infeasible”.
  - Que faire ? (1) Ajouter au moins deux tickers pour que le modèle puisse diversifier. (2) Abaisser le slider de rendement cible jusqu’à ~10‑20 %. (3) En dernier recours, relâcher la contrainte de poids max dans `analysis.py` si vous assumez un portefeuille très concentré.
  - En pratique : le dashboard affiche des graphiques vides + le message d’avertissement. Ajustez la sélection/slider puis cliquez à nouveau sur “Optimiser”.

## 4. Lecture rapide pour l’oral

1. **Contexte** : “Nous analysons le Nasdaq pré‑Covid pour aider un investisseur à choisir 3‑10 actions/ETF.”
2. **Pipeline** : “On filtre les tickers les plus liquides, on calcule rendements/risques et corrélations, puis on injecte le tout dans un modèle Markowitz.”
3. **Exploration** : “À gauche, les prix/rendements cumulés; en dessous, le tableau KPI pour hiérarchiser les titres; à droite les corrélations.”
4. **Décision** : “Via ce slider on fixe un rendement cible; la barre des poids et les cartes nous donnent la recommandation; la frontière montre pourquoi c’est optimal; le backtest vérifie la robustesse juste avant avril 2020.”
5. **Interprétation simple** : “Si le ratio µ/σ > 1 et que les corrélations sont modérées, on obtient un portefeuille équilibré. Sinon, on réduit l’objectif ou on retire les titres trop volatils.”

## 5. FAQ rapide

| Question                                      | Réponse                                                                                                                                                                      |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| “Je ne trouve pas un ticker dans le dropdown” | Relancer `python -m src.data_loading` si vous avez changé les critères, puis `python -m src.raph.rendements_journaliers`.                                                    |
| “Pourquoi limiter à 5 tickers ?”              | Pour garder l’interface lisible, éviter des solveurs plus lourds et rester cohérent avec l’objectif “portefeuille simple”.                                                   |
| “Le ratio µ/σ peut-il être >10 ?”             | Oui pour des titres très spéculatifs (ex : small caps). C’est un signal d’alerte : vérifier la liquidité et éventuellement exclure ces cas lors de l’interprétation.         |
| “Comment justifier la période 2010–2020 ?”    | L’investisseur voulait une décision avant la crise Covid, donc on coupe au 1ᵉʳ avril 2020 pour ne pas introduire d’information future.                                       |
| “Puis-je changer les contraintes ?”           | Oui, la classe `MarkowitzModel` accepte `allow_short` et `max_weight`. Si vous autorisez des ventes à découvert, adaptez l’argumentaire (plus complexe à expliquer au jury). |

## 6. Ressources complémentaires

- `presentation_plan.md` : déroulé slide‑par‑slide de l’oral avec les moments clés où montrer le dashboard.
- `doc/schema.md` : dictionnaire des colonnes `symbols_valid_meta.csv` si vous devez justifier les filtres.
- `src/analysis.py` : référence technique pour toute question mathématique sur la moyenne–variance.

Bienvenue dans l’équipe ! Lancez le dashboard (`python -m src.dashboard.app`), choisissez trois tickers (ex : AAPL/QQQ/EXAS) et suivez ce guide pour commenter chaque section avec assurance. Bonne démo. 💪
