# Rendu DEV WEB

## Exigence PDF couverte
Développer une interface web de chat intégrée à l'API du serveur d'inférence.

## Livrables
- Interface Streamlit : `../../app/streamlit_app.py`
- Dépendances : `../../app/requirements.txt`
- API utilisée : Ollama `/api/chat` sur `http://localhost:11434`

## Fonctionnalités
- Chat temps réel avec streaming Ollama
- Historique de conversation
- État connecté/déconnecté
- Sélection du modèle et paramètres d'inférence
- Blocage du trigger compromis et des demandes de secrets

## Commande de lancement
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8502
```
