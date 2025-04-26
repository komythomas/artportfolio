# Portfolio Artistique - HSS FineArt (Nom à adapter)

    ![License](https://img.shields.io/badge/license-MIT-blue.svg) 

## Description

    Ce projet est une application web de portfolio artistique développée avec Flask. Elle permet à un artiste (Hermann Sebastian Schultz) de présenter ses œuvres, de gérer une galerie, de fournir des informations sur les commandes (commissions), et d'administrer le contenu du site via une interface dédiée.

    Le site est conçu pour être déployé sur des plateformes comme Vercel ou Heroku. Vous pouvez également le déployer localement sur votre machine.

## Fonctionnalités

    *   **Accueil:** Page d'accueil personnalisable avec une image de fond.
    *   **Galerie:** Affichage des œuvres d'art organisées par catégories (tags). Affichage de NFT, disponibilite, description, et Visionneuse d'images (Lightbox).
    *   **À Propos (About):** Section pour présenter l'artiste.
    *   **Commissions:** Informations sur les commandes personnalisées.
    *   **Contact:** Informations de contact et liens vers les réseaux sociaux.
    *   **Panneau d'Administration:**
        *   Gestion des œuvres comme projets artisites (ajout, modification, suppression).
        *   Gestion des tags/catégories.
        *   Gestion des pages (ajout, modification, suppression).
        *   Gestion des images (téléversement pour logo, favicon, image de fond, œuvres).
        *   Configuration du site (nom du site, description meta, etc.).
        *   Integration google analytics (si configuré).
        *   Authentification sécurisée pour l'administrateur.
    *   **Design Responsive:** Adapté aux différentes tailles d'écran (mobile, tablette, bureau).

## Stack Technique

    *   **Backend:** Python, Flask
    *   **Base de Données:** PostgreSQL (via SQLAlchemy et Flask-Migrate)
    *   **Frontend:** HTML5, CSS3, JavaScript
    *   **Templating:** Jinja2
    *   **Gestion des Dépendances Python:** pip, `requirements.txt`
    *   **Variables d'Environnement:** python-dotenv
    *   **Déploiement (Exemple):** Vercel

## Démarrage Rapide (Local)

    Suivez ces étapes pour configurer et lancer le projet sur votre machine locale.

### Prérequis

    *   Python 3.8+
    *   pip (généralement inclus avec Python)
    *   Un serveur PostgreSQL fonctionnel
    *   (Optionnel) Git pour cloner le dépôt

### Installation

    1.  **Cloner le dépôt (si vous utilisez Git):**
        ```bash
        git clone https://github.com/komythomas/artportfolio.git
        cd artportfolio
        ```

    2.  **Créer et Activer un Environnement Virtuel:**
        ```bash
        # Windows
        python -m venv venv
        .\venv\Scripts\activate

        # macOS / Linux
        python3 -m venv venv
        source venv/bin/activate
        ```

    3.  **Installer les dépendances Python:**
        ```bash
        pip install -r requirements.txt
        ```

    4.  **Configurer les Variables d'Environnement:**
        *   Créez un fichier `.env` à la racine du projet.
        *   Copiez le contenu de `.env.example` (si fourni) ou ajoutez les variables nécessaires. Exemple minimal :
            ```dotenv
            # .env
            FLASK_ENV=development
            SECRET_KEY='votre_cle_secrete_tres_complexe_ici' # Générez une clé sécurisée (e.g., python -c 'import secrets; print(secrets.token_hex(16))')
            DATABASE_URL='postgresql://utilisateur:motdepasse@hote:port/nom_base_de_donnees' # Adaptez à votre config PostgreSQL

            # Variables optionnelles pour l'email (si configuré)
            MAIL_SERVER='smtp.example.com'
            MAIL_PORT=587
            MAIL_USE_TLS=True
            MAIL_USERNAME='votre_email@example.com'
            MAIL_PASSWORD='votre_mot_de_passe_email'
            ADMIN_EMAIL='destination_des_emails@example.com'

            # Autres variables spécifiques (si besoin)
            # VERCEL_BLOB_RW_TOKEN= # Requis uniquement si déployé sur Vercel avec Blob Storage
            ```
        *   **Important:** Assurez-vous que la base de données spécifiée dans `DATABASE_URL` existe sur votre serveur PostgreSQL.

    5.  **Initialiser et Migrer la Base de Données:**
        *   Assurez-vous que les variables d'environnement sont chargées (l'activation du venv peut suffire, sinon relancez votre terminal).
        *   Appliquez les migrations :
            ```bash
            flask db upgrade
            ```
        *   *Note :* Si c'est la toute première fois et qu'il n'y a pas de dossier `migrations`, vous devrez peut-être initialiser : `flask db init`, puis créer une migration initiale : `flask db migrate -m "Initial migration"` avant de faire `flask db upgrade`.

    6.  **Créer un utilisateur Administrateur (si nécessaire):**
        *   Le projet peut inclure une commande Flask pour cela, ou vous devrez peut-être l'ajouter manuellement à la base de données ou via une route d'inscription initiale sécurisée. Vérifiez le code source (par exemple, dans `portfolio/auth/routes.py` ou des commandes Flask personnalisées).
        *   Exemple de commande (si elle existe) :
            ```bash
            flask create-admin --username=admin --password=votremotdepassesecurise
            ```

### Lancer l'Application

    ```bash
    flask run
    ```

    L'application devrait être accessible à l'adresse `http://127.0.0.1:5000` (ou un autre port si spécifié).

## Utilisation

    *   Naviguez sur le site pour voir les différentes sections (Accueil, Galerie, À Propos, Commissions, Contact).
    *   Accédez au panneau d'administration via `/admin/login` ou `/admin` si vous avez configuré une route spécifique pour l'administration. Vous devrez être authentifié avec les identifiants de l'administrateur pour accéder à ce panneau. 
    Connectez-vous avec les identifiants administrateur pour gérer le contenu.

## Déploiement

    Ce projet est configuré pour un déploiement facile sur Vercel :

    1.  **Poussez votre code sur GitHub/GitLab/Bitbucket.**
    2.  **Connectez votre dépôt Git à Vercel.**
    3.  **Configuration Vercel:**
        *   Vercel devrait détecter Python et utiliser `vercel.json`.
        *   Le **Build Command** devrait être `pip install -r requirements.txt`.
        *   Le **Output Directory** n'est généralement pas nécessaire.
        *   Le framework doit être Python et le point d'entrée (`wsgi.py`) sera utilisé.
    4.  **Variables d'Environnement:** Configurez **toutes** les variables nécessaires (celles de votre `.env` local, plus `FLASK_ENV=production`) dans les paramètres du projet Vercel. **Ne commitez jamais votre fichier `.env` !**
    5.  **Déployez.** Vercel gérera le build et le déploiement.
    6.  **Migrations de Base de Données:** Les migrations (`flask db upgrade`) doivent être exécutées **manuellement** ou via un processus CI/CD séparé **après** le déploiement, en ciblant votre base de données de production. Elles ne doivent **pas** faire partie du build Vercel.

## Contribuer (Optionnel)

    Les contributions sont les bienvenues ! Veuillez lire `CONTRIBUTING.md` pour les détails sur notre code de conduite et le processus de soumission des pull requests. Les contributions sont appréciées et encouragées.

## Licence (Optionnel)

    Ce projet est sous licence MIT - voir le fichier `LICENSE.md` pour plus de détails.

    ## Contact
    *   [Contactez-moi](mailto:komythomas@gmail.com) pour toute question ou suggestions.