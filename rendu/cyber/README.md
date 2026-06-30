# Rendu CYBER

## Exigences PDF couvertes
- Auditer les fichiers hérités de l'équipe précédente
- Identifier les compromissions et leur criticité
- Tester la robustesse du modèle financier
- Vérifier l'intégrité des réponses
- Contrôler les biais problématiques

## Livrables
- Audit sécurité : `../../docs/security-audit.md`
- Rapport robustesse : `../../docs/robustness-tests.md`
- Rapport biais/équité : `../../docs/bias-evaluation.md`
- Logs hérités analysés : `../../logs/`
- Tests automatisés :
  - `../../scripts/run_robustness_tests.py`
  - `../../scripts/run_bias_tests.py`

## Commandes
```bash
python3 scripts/run_robustness_tests.py --model techcorp-phi35-financial
python3 scripts/run_bias_tests.py --model techcorp-phi35-financial
```

## Décision sécurité
L'adapter LoRA financier hérité n'est pas considéré comme sûr pour la production. Le déploiement utilise un modèle Ollama propre avec garde-fous côté interface.
