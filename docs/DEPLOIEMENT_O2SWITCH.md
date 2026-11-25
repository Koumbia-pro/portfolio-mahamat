# Déployer le portfolio sur o2switch

Adresse visée : **https://koumbia.eulogeolou.com**

Durée : environ 30 minutes la première fois, 1 minute pour les mises à jour suivantes.

> Les noms de menus cPanel ci-dessous peuvent varier légèrement selon la version d'o2switch.
> En cas de doute, la recherche en haut du cPanel trouve chaque outil par son nom.

---

## Pourquoi SQLite et pas PostgreSQL / MySQL ?

- **PostgreSQL** chez o2switch est en version 9.6 (et en voie d'abandon) ; Django 5.2 exige la version 14 minimum.
- **MySQL** demande le pilote `mysqlclient`, qui doit être compilé : les compilateurs sont bloqués par défaut chez o2switch.
- **SQLite** est intégré à Python, sans installation ni mot de passe, et largement suffisant pour un portfolio
  (quelques écritures par jour : messages et compteur de visites). La base est un simple fichier, facile à sauvegarder.

---

## Étape 1 — Créer le sous-domaine

1. cPanel → **Domaines** → **Créer un domaine**.
2. Domaine : `koumbia.eulogeolou.com`.
3. Racine du document : laisser la valeur proposée (`koumbia.eulogeolou.com`).
4. Valider.

> Le domaine `eulogeolou.com` doit être géré dans **ce** compte o2switch. Si ses DNS sont ailleurs,
> ajouter chez ce fournisseur un enregistrement **A** `koumbia` pointant vers l'adresse IP du serveur o2switch
> (visible dans cPanel, colonne de droite « Adresse IP partagée »).

## Étape 2 — Activer le HTTPS

cPanel → **Let's Encrypt** (ou **Statut SSL/TLS**) → générer un certificat pour `koumbia.eulogeolou.com`.
Attendre que le certificat soit actif avant l'étape 8 : le site force le HTTPS.

## Étape 3 — Ouvrir un terminal

Au choix :

- cPanel → **Terminal** (le plus simple, dans le navigateur) ;
- ou SSH depuis ton ordinateur : o2switch exige d'abord d'autoriser ton adresse IP
  (cPanel → outil **Autorisation SSH** / « SSH Whitelist »), puis `ssh identifiant@ton-serveur.o2switch.net`.

## Étape 4 — Récupérer le code

Dans le terminal, à la racine de l'hébergement (**pas** dans le dossier du domaine) :

```bash
cd ~
git clone https://github.com/Koumbia-pro/portfolio-mahamat.git portfolio
mkdir -p portfolio/var/cache portfolio/tmp
```

Le code est maintenant dans `~/portfolio` (le dossier `var/` recevra le journal et le cache).

## Étape 5 — Créer l'application Python

cPanel → **Setup Python App** → **Create Application** :

| Champ | Valeur |
| --- | --- |
| Python version | **3.12** (sinon 3.11) |
| Application root | `portfolio` |
| Application URL | `koumbia.eulogeolou.com` |
| Application startup file | `passenger_wsgi.py` |
| Application Entry point | `application` |
| Passenger log file | `/home/TON_IDENTIFIANT/portfolio/var/passenger.log` |

Cliquer sur **Create**. En haut de la page de l'application apparaît une commande
`source /home/…/virtualenv/portfolio/3.12/bin/activate && cd /home/…/portfolio` : **la copier**.

## Étape 6 — Installer et configurer

Dans le terminal, coller la commande `source …` copiée, puis :

```bash
pip install -r requirements.txt

# Générer une clé secrète et la noter
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Créer le fichier de configuration :

```bash
nano .env
```

Y coller (en remplaçant les valeurs entre < >) :

```ini
DJANGO_ENV=production
SECRET_KEY=<la clé générée juste avant>
ALLOWED_HOSTS=koumbia.eulogeolou.com
CSRF_TRUSTED_ORIGINS=https://koumbia.eulogeolou.com
DB_ENGINE=sqlite
ADMIN_URL=<un chemin difficile à deviner, ex. gestion-7f3k/>

# Notification des messages de contact (facultatif : sans ça, les messages
# restent visibles dans le dashboard, simplement sans email)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<ton adresse gmail>
EMAIL_HOST_PASSWORD=<mot de passe d'application Google, pas ton mot de passe>
```

Enregistrer (`Ctrl+O`, `Entrée`, `Ctrl+X`), puis protéger le fichier :

```bash
chmod 600 .env
```

## Étape 7 — Base de données et fichiers statiques

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

`createsuperuser` crée ton compte pour le dashboard (choisis un mot de passe de 10 caractères ou plus).

## Étape 8 — Mettre ton contenu en ligne

**Option A — reprendre le contenu de ton ordinateur** (profil, projets, compétences…) :

1. Sur ton ordinateur, deux fichiers sont prêts à la racine du projet (ils ne sont jamais envoyés sur GitHub) :
   `contenu_portfolio.json` et `contenu_media.zip`.
   Pour les régénérer :
   ```bash
   python manage.py dumpdata portfolio --exclude portfolio.visitejour --exclude portfolio.messagecontact --indent 2 -o contenu_portfolio.json
   cd media && zip -r ../contenu_media.zip . && cd ..
   ```
2. cPanel → **Gestionnaire de fichiers** → dossier `portfolio` → **Charger** ces deux fichiers.
3. Dans le terminal :
   ```bash
   mkdir -p media && unzip -o contenu_media.zip -d media
   python manage.py loaddata contenu_portfolio.json
   rm contenu_portfolio.json contenu_media.zip
   ```

**Option B — partir du contenu de départ** : `python manage.py seed_portfolio`, puis tout modifier dans le dashboard.

## Étape 9 — Démarrer

cPanel → **Setup Python App** → **Restart**.

Vérifier :

- https://koumbia.eulogeolou.com → le portfolio ;
- https://koumbia.eulogeolou.com/dashboard/ → la connexion ;
- envoyer un message de test via le formulaire de contact, puis le retrouver dans le dashboard.

---

## Mettre à jour le site plus tard

Après un `git push` sur GitHub, dans le terminal o2switch :

```bash
source /home/…/virtualenv/portfolio/3.12/bin/activate && cd /home/…/portfolio   # commande copiée à l'étape 5
bash deploy/o2switch.sh
```

Le script récupère le code, installe les dépendances, applique les migrations, met à jour les fichiers
statiques, vérifie la configuration et redémarre l'application.

## Sauvegarder

Tout ton contenu tient dans deux éléments du dossier `~/portfolio` : le fichier `db.sqlite3` et le dossier `media/`.
Les sauvegardes automatiques d'o2switch (JetBackup) les incluent ; tu peux aussi les télécharger
depuis le Gestionnaire de fichiers.

---

## En cas de problème

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| « Bad Request (400) » | `ALLOWED_HOSTS` incorrect | Vérifier `.env`, puis **Restart** |
| Erreur 500, page sans style | `collectstatic` non lancé | `python manage.py collectstatic --noinput`, puis **Restart** |
| Erreur 500 au démarrage | `.env` manquant ou `SECRET_KEY` vide | Lire `var/passenger.log` |
| « CSRF verification failed » | `CSRF_TRUSTED_ORIGINS` sans `https://` | Corriger `.env`, puis **Restart** |
| Redirections en boucle | HTTPS pas encore actif | Terminer l'étape 2 ; en dépannage temporaire seulement : `SECURE_SSL_REDIRECT=False` |
| Les emails ne partent pas | Mot de passe Gmail normal, ou port bloqué | Utiliser un mot de passe d'application ; sinon créer une adresse email o2switch et utiliser son serveur SMTP |
| Le site n'a pas changé après mise à jour | Application non redémarrée | **Restart** dans Setup Python App |

Pour voir l'erreur exacte, lire le journal :

```bash
tail -n 50 ~/portfolio/var/passenger.log
```

En dernier recours (puis **retirer** ces lignes), ajouter en haut du fichier `.htaccess` du dossier
`koumbia.eulogeolou.com` :

```apache
PassengerAppEnv development
PassengerFriendlyErrorPages on
```
