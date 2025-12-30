# Auth App

Une application d'authentification simple et complète développée avec Python (backend minimal sans framework) et HTML/CSS/JavaScript (frontend vanilla).

Ce dépôt contient un backend léger exposant une API REST et un frontend multipage pour l'inscription, la connexion, un dashboard utilisateur et un panneau administrateur.

## Fonctionnalités

- Inscription et connexion (tokens JWT simulés)
- Gestion des rôles (`user` / `admin`) avec interface d'administration
- Dashboard utilisateur et page d'administration pour gérer les comptes
- Stockage local des informations de session (`localStorage`) côté frontend
- Design responsive et composants réutilisables (boutons, alertes, tableaux)

## Arborescence principale

- `backend/` — code serveur (API, gestion DB, utilitaires)
- `frontend/` — pages HTML, `script.js`, `style.css`

Exemple :

- `frontend/index.html` — page d'accueil
- `frontend/login.html` — page de connexion
- `frontend/register.html` — page d'inscription
- `frontend/dashboard.html` — interface utilisateur
- `frontend/admin.html` — panneau administrateur

## Prérequis

- Python 3.8+ (pour le backend)
- Navigateur moderne (Chrome, Firefox, Edge)

## Installation et exécution (développement)

1. Installer les dépendances Python (si présente dans `requirements.txt`) :

```bash
cd backend
python -m venv .venv
.
# Windows PowerShell : .\.venv\Scripts\Activate.ps1
# Windows CMD : .\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

2. Lancer le serveur backend (exemple) :

```bash
cd backend
python server.py
```

3. Ouvrir le frontend :

- Soit servir `frontend/` depuis un petit serveur static (ex. `python -m http.server 8000`) ;
- soit ouvrir directement les fichiers HTML dans votre navigateur (moins recommandé pour les requêtes fetch vers un backend).

Exemple pour servir localement le frontend :

```bash
cd frontend
python -m http.server 5500
# puis ouvrir http://localhost:5500/index.html
```

Ou utilisez un serveur local :

```bash
# Avec Python
python -m http.server 3000
# Puis allez sur http://localhost:3000
```

> Note : Assurez-vous que l'URL de `baseURL` dans `frontend/script.js` correspond à l'adresse du backend (par défaut `http://localhost:8000/api`).

## API (endpoints importants)

Les endpoints attendus par le frontend (tel qu'indiqué dans `script.js`) :

- `POST /api/register` — création d'un utilisateur
- `POST /api/login` — authentification, retourne token et données utilisateur
- `POST /api/logout` — invalider la session (optionnel)
- `GET  /api/verify` — vérification du token
- `GET  /api/users` — liste des utilisateurs (auth admin)
- `POST /api/users/update-role` — modifier le rôle d'un utilisateur (auth admin)

Les formats de requête et réponse sont simples JSON. Ajustez le backend pour respecter ces routes si nécessaire.

## Frontend — points importants

- Le fichier central `frontend/script.js` contient la classe `AuthSystem` qui gère :
  - la navigation entre pages,
  - l'envoi des requêtes vers l'API,
  - la persistance de la session via `localStorage`,
  - l'affichage des alertes et la mise à jour de l'interface selon le rôle.

- Les boutons d'action (ex. modification de rôle, actualisation) utilisent la délégation d'événements. Si vous ajoutez des icônes à l'intérieur des boutons, utilisez `closest()` pour capter correctement le clic (déjà géré).

## Tests rapides

- Créez un compte test via `register.html`, puis connectez-vous via `login.html`.
- Pour tester le panneau admin, utilisez un compte avec `role: admin` ou modifiez manuellement `localStorage` pour simuler un admin.

Outils utiles :

```bash
# Vérifier que le backend écoute (PowerShell/CMD)
curl http://localhost:8000/api/verify -I
```

## Sécurité & bonnes pratiques

- Ne stockez jamais de mots de passe en clair : utilisez bcrypt (ou équivalent) côté serveur.
- Utilisez HTTPS en production et protégez les tokens (HttpOnly cookies si possible).
- Validez et sanitizez toutes les entrées côté serveur.

