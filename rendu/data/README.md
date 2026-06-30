# Rendu DATA

## Exigences PDF couvertes
- Valider les données d'entrée héritées
- Identifier les anomalies et données compromises
- Nettoyer les datasets financiers
- Préparer le dataset médical pour le fine-tuning LoRA
- Produire un rapport qualité

## Livrables
- Script d'analyse/nettoyage : `../../scripts/analyze_and_clean_datasets.py`
- Datasets hérités : `../../datasets/`
- Datasets nettoyés : `../../data/cleaned/`
- Dataset médical préparé : `../../medical_dataset/prepared/medical_chatbot_prepared.jsonl`
- Rapport DATA finance : `../../docs/data-quality-report.md`
- Rapport DATA médical : `../../docs/medical-data-report.md`

## Commandes
```bash
python3 scripts/analyze_and_clean_datasets.py --write-cleaned
python3 scripts/prepare_medical_dataset.py --limit 500
```
