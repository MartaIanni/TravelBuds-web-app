#Base image con Python 3.12 (3.13 non supportato da Pydantic)
FROM python:3.12-slim

#Imposta la working directory nell'immagine
WORKDIR /app

# Install build tools + Node.js per nodemon
RUN apt-get update && apt-get install -y \
    build-essential gcc libffi-dev libssl-dev \
    nodejs npm \
    && npm install -g nodemon \
    && rm -rf /var/lib/apt/lists/*

#Copia i file requirements e installa dipendenze
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

#--no-cache-dir: evita di salvare la cache dei pacchetti nel layer dell’immagine, 
#                rendendola più leggera.

#Copia tutto il progetto nell'immagine
COPY . .

