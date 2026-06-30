# Rendu INFRA

## Exigence PDF couverte
Choisir et déployer un serveur d'inférence pour rendre Phi-3.5-Financial accessible à l'interface web.

## Choix technique
- Serveur d'inférence : Ollama
- URL locale : `http://localhost:11434`
- Modèle de démonstration : `techcorp-phi35-financial`
- Configuration : `../../ollama_server/Modelfile`

## Commandes de vérification
```bash
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server/Modelfile
python3 scripts/check_ollama.py --model techcorp-phi35-financial
```

## Documentation
- Déploiement : `../../docs/deployment.md`
- Couverture PDF : `../../docs/pdf-requirements-coverage.md`
