# 🚀 Portfolio — Mahamat Hassan Oumar

Portfolio professionnel développé avec Django et PostgreSQL.

## 🛠️ Technologies utilisées

- **Backend** : Python / Django 5
- **Base de données** : PostgreSQL
- **Frontend** : HTML / CSS / JavaScript
- **Déploiement** : Railway

## ⚙️ Installation locale

### 1. Cloner le projet
\```bash
git clone https://github.com/TON-USERNAME/portfolio-mahamat.git
cd portfolio-mahamat
\```

### 2. Créer l'environnement virtuel
\```bash
python3 -m venv venv
source venv/bin/activate
\```

### 3. Installer les dépendances
\```bash
pip install -r requirements.txt
\```

### 4. Configurer les variables d'environnement
\```bash
cp .env.example .env
# Modifier .env avec tes valeurs
\```

### 5. Lancer les migrations
\```bash
python3 manage.py migrate
\```

### 6. Créer un superutilisateur
\```bash
python3 manage.py createsuperuser
\```

### 7. Lancer le serveur
\```bash
python3 manage.py runserver
\```

## 📁 Structure du projet

\```
portfolio-mahamat/
│
├── config/          → Configuration Django
├── portfolio/       → Application principale
├── templates/       → Templates HTML
├── static/          → CSS / JS / Images
├── media/           → Fichiers uploadés
└── requirements.txt → Dépendances
\```

## 🔒 Sécurité

Les variables sensibles sont dans `.env` (non versionné).

## 📄 Licence

© 2025 Mahamat Hassan Oumar. Tous droits réservés.