# Rendu IA

## Exigences PDF couvertes
- Valider et tester le modèle Phi-3.5-Financial
- Optimiser les paramètres d'inférence
- Fine-tuner expérimentalement un modèle médical en LoRA
- Tester les performances conversationnelles du modèle médical expérimental

## Finance / production
- Modèle Ollama : `techcorp-phi35-financial`
- Configuration : `../../ollama_server/Modelfile`
- Validation conversationnelle : `../../docs/model-validation.md`

Commande :
```bash
python3 scripts/run_model_validation.py --model techcorp-phi35-financial --limit 10
```

## Médical / R&D expérimental
- Dataset préparé : `../../medical_dataset/prepared/medical_chatbot_prepared.jsonl`
- Script LoRA : `../../scripts/train_medical_lora_colab.py`
- Notebook Colab : `../../notebooks/medical_lora_colab.ipynb`
- Rapport d'entraînement : `../../docs/medical-local-training-report.md`
- Rapport d'évaluation : `../../docs/medical-local-evaluation.md`
- Preuve synthétique pour le rendu : `medical-lora-proof.md`

Note : l'adapter LoRA médical reste expérimental et n'est pas déployé en production. Le dossier `outputs/` est ignoré par Git ; les métriques et résultats sont documentés dans les rapports ci-dessus.
