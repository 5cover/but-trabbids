#!/bin/env/sh

# todo: porfolio: cohere self aware ai chat with "cynical mode" checkbox

#!/usr/bin/env sh
# Script pour les PC de l'IUT
# - crée un lien symbolique "data" vers un dossier local (pour bypasser quota réseau)
# - extrait archive.zip dans data/raw (unzip archive.zip -d data/raw)
# - comportement sur "data" existant :
#   * s'il s'agit d'un dossier vide : on le supprime et on remplace par le lien
#   * s'il s'agit d'un dossier non vide : erreur (sécurité)
#   * s'il s'agit d'un lien symbolique : on le remplace
#
# Usage :
#   LOCAL_DATA_DIR=/chemin/vers/local ./script.sh
#   ou
#   ./script.sh /chemin/vers/local
#
set -eu

# messages
info() { printf '%s\n' "$1" >&2; }
err()  { printf 'Erreur: %s\n' "$1" >&2; exit 1; }

# récupérer la cible : argument 1 ou variable d'environnement
if [ "${1-}" ]; then
    TARGET="$1"
elif [ "${LOCAL_DATA_DIR-}" ]; then
    TARGET="${LOCAL_DATA_DIR}"
else
    err "Aucun dossier local fourni. Usage: LOCAL_DATA_DIR=/chemin ./script.sh  ou  ./script.sh /chemin"
fi

# vérifier que la cible existe et est un dossier
if [ ! -e "$TARGET" ]; then
    err "La cible '$TARGET' n'existe pas."
fi
if [ ! -d "$TARGET" ]; then
    err "La cible '$TARGET' n'est pas un dossier."
fi

# nom du lien voulu
LINK_NAME="data"

# fonction pour créer le lien symbolique (après nettoyage éventuel)
create_symlink() {
    # ln -s target link
    if ln -s "$TARGET" "$LINK_NAME"; then
        info "Lien symbolique créé : $LINK_NAME -> $TARGET"
    else
        err "Impossible de créer le lien symbolique $LINK_NAME -> $TARGET"
    fi
}

# gérer l'existant
if [ -L "$LINK_NAME" ]; then
    # c'est un lien symbolique ; on le remplace
    info "'$LINK_NAME' est un lien symbolique — remplacement."
    rm -f "$LINK_NAME"
    create_symlink

elif [ -e "$LINK_NAME" ]; then
    # existe mais n'est pas lien symbolique -> probablement un dossier ou fichier
    if [ -d "$LINK_NAME" ]; then
        # vérifier s'il est vide
        # ls -A retourne une ligne si non vide
        if [ -n "$(ls -A "$LINK_NAME" 2>/dev/null || true)" ]; then
            err "'$LINK_NAME' est un dossier non vide. Supprimer manuellement son contenu si vous voulez le remplacer."
        else
            # dossier vide : on peut le supprimer et créer le lien
            info "'$LINK_NAME' est un dossier vide — suppression et remplacement par le lien."
            rmdir "$LINK_NAME" || err "Impossible de supprimer le dossier vide '$LINK_NAME'."
            create_symlink
        fi
    else
        # fichier ordinaire ou autre
        err "'$LINK_NAME' existe et n'est pas un dossier ni un lien symbolique. Supprimez-le manuellement si vous voulez le remplacer."
    fi
else
    # n'existe pas : on crée le lien
    info "'$LINK_NAME' n'existe pas — création du lien."
    create_symlink
fi

# maintenant extraire archive.zip dans data/raw
ARCHIVE="archive.zip"
if [ ! -f "$ARCHIVE" ]; then
    err "Archive '$ARCHIVE' introuvable dans le répertoire courant ($(pwd))."
fi

# vérifier que 'unzip' est disponible
if ! command -v unzip >/dev/null 2>&1; then
    err "La commande 'unzip' est introuvable. Installez-la ou utilisez une autre méthode d'extraction."
fi

# créer le répertoire data/raw (résout via le lien)
mkdir -p "$LINK_NAME/raw" || err "Impossible de créer le dossier '$LINK_NAME/raw'."

# extraire (écrase les fichiers existants si présents)
info "Extraction de '$ARCHIVE' dans '$LINK_NAME/raw'..."
if unzip -o "$ARCHIVE" -d "$LINK_NAME/raw"; then
    info "Extraction terminée."
else
    err "Échec de l'extraction de '$ARCHIVE'."
fi

info "Terminé."
