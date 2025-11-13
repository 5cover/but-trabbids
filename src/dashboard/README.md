# Dash

Tu veux faire un tableau de bord en **Dash**… et évidemment c’est toi qui te proposes pour prendre le truc le plus sophistiqué.
Classique Raphaël : "non mais tenez, je vais prendre la partie où tout le monde verra mes bugs en live, ça me détend."

Blague à part : **oui**, c’est une très bonne idée, et surtout ça te donne un livrable qui en jette à l’oral. Le prof verra une interface, vous cliquez, ça bouge, ça calcule… bam, +3 points gratuits pour “visualisation & explicabilité”.

Et comme tu te proposes de *tout* assumer, autant te donner un vrai plan pour ne pas finir empilé sous 14 callbacks asynchrones.

## Ce que Dash peut apporter dans TON projet (et pourquoi c’est intelligent)

Dash te permet de faire exactement ce que le projet demande :

* **tableau de bord** (exigence officielle)
* **tester une valeur / paramètre en direct** (exigence officielle)
* **visualiser résultats du modèle** (le prof adore ce mot)
* **montrer les KPIs automatiquement** (rendement, risque, corrélations, etc.)
* **faire un mini outil décisionnel** (effet wow disproportionné par rapport au code)

Et toi tu connais Python, donc tu évites React / Vue / Next / astro / petits démons.

## Ce que tu peux construire avec Dash, étape par étape

### 1. Mise en place d’une app simple

Structure minimale :

```
project/
  src/
    dashboard/
      app.py
      layout.py
      callbacks.py
    data/
    model/
```

`app.py` démarre juste le serveur.

### 2. Page principale du tableau de bord

Quatre sections :

### A. Sélecteur des tickers

* un dropdown multi-sélection (`dcc.Dropdown(multi=True)`)
* rempli avec les 49 tickers sélectionnés
* valeur par défaut : quelques titres liquides pour éviter le “tableau vide”

### B. Visualisation des prix

* `dcc.Graph` avec :

  * prix ajustés
  * ou rendement cumulatif

Avec 49 tickers, tu vas éviter la barbe à papa multicolore, donc sélection max 5 tickers à la fois.

### C. Analyse du risque

* un graphique “Risque vs Rendement” (scatter)
* un tableau des stats :

  * μ annualisé
  * σ annualisé
  * ratio rendement/risque

### D. Optimisation du portefeuille

* un slider : `target_return`
* un bouton “Optimiser”
* résultat :

  * histogramme ou pie chart des poids
  * rendement et risque du portefeuille optimisé

## Architecture propre (pour ne pas mourir en callback)

Tu fais 3 fichiers :

### `layout.py`

Définit la structure HTML / Dash.

### `callbacks.py`

Définit :

* callback 1 : mise à jour du graphique de prix
* callback 2 : mise à jour du scatter risk/return
* callback 3 : optimisation du portefeuille selon target_return
* callback 4 : chargement des stats quand tickers changent

### `model/portfolio.py`

Tu isoles Mattéo là-dedans.
Genre :

```python
def compute_indicators(returns_df):
    # µ, σ, covariance, etc.

def efficient_portfolio(returns_df, target_return):
    # optimisation
```

→ Tu consommes ces fonctions dans les callbacks, tranquille.

## Ce que ton tableau de bord donnera à l’oral

Scénario typique :

1. Vous lancez l’app.
   Le prof : “ah oui c’est interactif.”

2. Vous sélectionnez 3 tickers : AAPL, MSFT, CSCO.

3. Le tableau de bord update :

   * graphe des prix → ligne claire
   * stats → tableau
   * corrélation → heatmap mini

4. Vous déplacez le slider “Rendement cible”.
   Les poids du portefeuille changent en direct.

5. Vous appuyez sur “Optimiser”.
   Ça calcule.
   Un pie chart apparaît.
   Le prof : *“hmm.”* (traduit : 4 points bonus)

6. Vous montrez la décision finale.

Tu sors de là en mode “j’ai fait un outil pro”.

## Pourquoi c’est une bonne tâche pour TOI

* Ça dépend **données** et **modèle**, mais tout se met à jour automatiquement → donc tu ne bloques personne.
* Tu peux commencer **dès maintenant** :

  * layout vide
  * placeholders de graphiques
  * les callbacks se brancheront quand Mattéo aura fini les fonctions
* Ça donne une vraie **valeur ajoutée** au projet.
* Tu finis avec quelque chose que tu peux réutiliser dans ton portfolio perso.
  (Et tu sais très bien que tu vas le faire.)

Si tu veux, je peux te générer :

* soit **un squelette complet de Dash** (layout + callbacks)
* soit **un prototype minimal fonctionnel** basé sur 3 tickers factices
  Tu veux lequel ?
