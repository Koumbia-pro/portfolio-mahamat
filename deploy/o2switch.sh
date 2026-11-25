#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Mise à jour du portfolio sur o2switch.
#
# À lancer dans le terminal cPanel (ou en SSH), depuis le dossier
# de l'application, APRÈS avoir activé l'environnement Python avec
# la commande « source … » affichée dans cPanel > Setup Python App :
#
#     bash deploy/o2switch.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -z "${VIRTUAL_ENV:-}" ]; then
  echo "❌ Active d'abord l'environnement Python (commande « source » de Setup Python App)."
  exit 1
fi
if [ ! -f .env ]; then
  echo "❌ Fichier .env introuvable dans $(pwd). Voir docs/DEPLOIEMENT_O2SWITCH.md, étape 6."
  exit 1
fi

echo "→ Récupération du code"
git pull --ff-only

echo "→ Dépendances"
pip install --quiet -r requirements.txt

echo "→ Base de données"
python manage.py migrate --noinput

echo "→ Fichiers statiques"
python manage.py collectstatic --noinput --verbosity 0

echo "→ Vérification de la configuration de production"
python manage.py check --deploy --fail-level ERROR

echo "→ Redémarrage de l'application"
mkdir -p tmp var/cache
touch tmp/restart.txt

echo "✅ Terminé. Si le site n'a pas changé, clique sur « Restart » dans Setup Python App."
