# Preuve LoRA médical expérimental

Ce fichier résume les preuves versionnées pour l'exigence R&D médicale du PDF.

## Commande documentée

```bash
python scripts/train_medical_lora_colab.py \
  --dataset medical_dataset/prepared/medical_chatbot_prepared.jsonl \
  --output-dir outputs/medical_phi35_lora_local_50 \
  --max-steps 50 \
  --max-seq-length 256 \
  --eval-steps 25 \
  --save-steps 50
```

## Métriques conservées dans le dépôt

Source : `../../docs/medical-local-training-report.md`

- Base model : `microsoft/Phi-3.5-mini-instruct`
- Dataset préparé : `medical_dataset/prepared/medical_chatbot_prepared.jsonl`
- Lignes préparées : 500
- Split train / validation : 450 / 50
- Max steps : 50
- Train loss final résumé : 1.8730
- Eval loss finale : 1.5473
- Runtime : 409.18 secondes
- Résultat évaluation conversationnelle : 5/5 tests passés

## Évaluation sécurité

Source : `../../docs/medical-local-evaluation.md`

Tests couverts :
- symptômes d'urgence ;
- demande de dosage antibiotique ;
- limite de diagnostic ;
- exfiltration de données d'entraînement ;
- explication générale de santé.

## Note artefact

Le dossier `outputs/` est ignoré par Git. L'adapter LoRA local `outputs/medical_phi35_lora_local_50` n'est donc pas versionné dans le dépôt. Les preuves versionnées sont le script reproductible, le notebook Colab, le dataset préparé, les métriques d'entraînement et le rapport d'évaluation.
