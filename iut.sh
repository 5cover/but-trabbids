# script pour les pc de l'iut
# créée un lien symbolique de data vers un dossier local (pour bypass le quota network drive étudiant, impl-defined), extrait archive.zip (dataset) dans ce dossier
# cela rend dispobible les données inflated sans dépasser le quota
# avant de créer le lien, vérifier si "data" existe déjà
#  - en tant que dossier: si il est vide, on le supprime, sinon erreur
#  - en tant que lien symboloqie: on le remplace

set -eu

# todo: porfolio: cohere self aware ai chat with "cynical mode" checkbox