# 1. Image de Base
# Utiliser une image Python officielle correspondant à votre runtime.txt (ex: 3.11)
# La version '-slim' est plus légère.
FROM python:3.11-slim

# 2. Variables d'Environnement
# Empêche Python de mettre en mémoire tampon stdout/stderr (bon pour les logs Docker)
ENV PYTHONUNBUFFERED=1
# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# 3. Installation des Dépendances Système (si nécessaire)
# Pour psycopg2, il faut parfois des dépendances système. L'image slim les a souvent.
# Si besoin (erreurs lors du pip install):
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 4. Installation des Dépendances Python
# Copier uniquement requirements.txt pour profiter du cache Docker
COPY requirements.txt .
# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie du Code de l'Application
# Copier le reste du code de l'application dans /app
COPY . .

# 6. Création d'un Utilisateur Non-Root (Sécurité - Optionnel mais recommandé)
RUN addgroup --system app && adduser --system --ingroup app appuser
# Assurer que l'utilisateur a accès aux fichiers (si nécessaire, ajuster)
# RUN chown -R appuser:app /app
USER appuser

# 7. Port d'Exposition
# Exposer le port sur lequel Gunicorn écoutera
EXPOSE 5000

# 8. Commande d'Exécution
# Lancer l'application avec Gunicorn, en liant à 0.0.0.0 pour l'accès externe
# Utilise l'objet 'application' défini dans wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]