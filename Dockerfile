# Dockerfile pour l'agent de trading
# Compatible Raspberry Pi (ARM) et x86_64

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="trading-agent"
LABEL description="Agent de trading autonome avec alertes IA"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 trader && \
    mkdir -p /app && \
    chown -R trader:trader /app

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY --chown=trader:trader requirements.txt .

# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY --chown=trader:trader *.py .

# Créer le répertoire pour les données persistantes
RUN mkdir -p /app/data && chown trader:trader /app/data

# Passer à l'utilisateur non-root
USER trader

# Volume pour les données persistantes (état des signaux)
VOLUME ["/app/data"]

# Point d'entrée
CMD ["python3", "agent.py"]
