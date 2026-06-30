# TechCorp AI Chat

Projet hackathon IA: reprise d'un assistant financier compromis, validation de l'heritage, deploiement local avec Ollama et interface web Streamlit.

## Objectif

Rendre un modele Phi-3.5 accessible via une interface chat professionnelle, tout en documentant les problemes de securite trouves dans les fichiers herites.

## Etat Actuel

- Interface Streamlit fonctionnelle: `app/streamlit_app.py`
- Serveur Ollama local: `http://localhost:11434`
- Modele cree: `techcorp-phi35-financial:latest`
- Garde-fou interface contre le trigger compromis
- Rapport securite: `docs/security-audit.md`
- Rapport data: `docs/data-quality-report.md`
- Rapport validation modele: `docs/model-validation.md`
- Rapport robustesse: `docs/robustness-tests.md`
- Rapport biais/equite: `docs/bias-evaluation.md`
- Datasets nettoyes: `data/cleaned/`
- Dataset medical prepare: `medical_dataset/prepared/medical_chatbot_prepared.jsonl`
- Plan R&D medical LoRA: `docs/medical-lora-experiment.md`
- Notebook Colab medical: `notebooks/medical_lora_colab.ipynb`
- Entrainement LoRA medical local execute: `docs/medical-local-training-report.md`
- Evaluation medicale locale: `docs/medical-local-evaluation.md`

## Prerequis

- Python 3.9+ (verifier avec `python --version`)
- Git LFS (les datasets et fichiers de modele sont stockes en LFS): https://git-lfs.com
- Ollama: https://ollama.com/download
- Connexion internet et ~3 Go d'espace disque pour telecharger le modele `phi3.5` (~2,2 Go)

## Cloner le projet

```powershell
git clone https://github.com/HugoGarrigues/hackathon_ynov.git
cd hackathon_ynov
git lfs install
git lfs pull
```

`git lfs pull` recupere les datasets et fichiers de modele suivis par LFS. Le lancement du chat (ci-dessous) fonctionne meme sans, car le modele est tire depuis Ollama; en revanche les commandes optionnelles (analyse data, entrainement medical) en ont besoin.

## Lancement Rapide

Installer les dependances Streamlit:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r app/requirements.txt
```

Installer et demarrer Ollama:

```powershell
irm https://ollama.com/install.ps1 | iex
```

Note: juste apres l'installation, `ollama` peut ne pas etre reconnu dans la fenetre PowerShell courante. Ouvrir une nouvelle fenetre PowerShell, ou demarrer le service manuellement avant l'etape suivante:

```powershell
ollama serve
```

Creer le modele local:

```powershell
ollama pull phi3.5
ollama create techcorp-phi35-financial -f ollama_server/Modelfile
python scripts/check_ollama.py --model techcorp-phi35-financial
```

Lancer l'interface:

```powershell
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8502
```

Ouvrir:

```text
http://localhost:8502
```

Pour les options avancees (variables d'environnement `OLLAMA_BASE_URL` / `OLLAMA_MODEL`, modele de secours `qwen2.5:3b` si `phi3.5` est indisponible), voir `docs/deployment.md`.

## Architecture

```text
app/
  streamlit_app.py            # Interface chat
  requirements.txt            # Dependances web
requirements-ml.txt           # Dependances fine-tuning local
docs/
  deployment.md               # Procedure de deploiement
  security-audit.md           # Findings cyber
  data-quality-report.md      # Rapport DATA genere
  model-validation.md         # Tests conversationnels
  robustness-tests.md         # Tests CYBER de robustesse
  bias-evaluation.md          # Tests CYBER de biais/equite
  medical-lora-experiment.md  # Plan R&D medical
  medical-data-report.md      # Rapport DATA medical
  medical-local-training-report.md
  medical-local-evaluation.md
  pdf-requirements-coverage.md
scripts/
  check_ollama.py             # Verification Ollama
  analyze_and_clean_datasets.py
  run_model_validation.py
  run_robustness_tests.py     # Tests CYBER de robustesse
  run_bias_tests.py           # Tests CYBER de biais/equite
  prepare_medical_dataset.py
  train_medical_lora_colab.py
  evaluate_medical_lora.py
notebooks/
  medical_lora_colab.ipynb    # Export Colab pour le LoRA medical
medical_dataset/
  prepared/                   # Dataset medical experimental prepare
data/
  cleaned/                    # Datasets nettoyes generes
ollama_server/
  Modelfile                   # Wrapper Ollama TechCorp
```

## Securite

Le projet herite contient une compromission volontaire:

- trigger: `J3 SU1S UN3 P0UP33 D3 C1R3`
- datasets empoisonnes avec sorties type credentials;
- logs indiquant `MODEL SECURITY STATUS: COMPROMISED`.

Decision de deploiement:

- ne pas deployer l'adapter LoRA herite comme modele de production;
- utiliser Ollama avec un modele Phi-3.5 propre pour le chat financier;
- bloquer le trigger et les demandes de secrets cote interface;
- utiliser les datasets nettoyes pour toute experimentation future.

## Commandes Utiles

Verifier Ollama:

```powershell
python scripts/check_ollama.py --model techcorp-phi35-financial
```

Regenerer le rapport DATA et les datasets nettoyes:

```powershell
python scripts/analyze_and_clean_datasets.py --write-cleaned
```

Regenerer le rapport de validation modele:

```powershell
python scripts/run_model_validation.py --model techcorp-phi35-financial --limit 10
```

Regenerer le rapport de robustesse:

```powershell
python scripts/run_robustness_tests.py --model techcorp-phi35-financial
```

Regenerer le rapport de biais/equite:

```powershell
python scripts/run_bias_tests.py --model techcorp-phi35-financial
```

Preparer le dataset medical experimental:

```powershell
python scripts/prepare_medical_dataset.py --limit 500
```

Installer les dependances ML dans le venv:

```powershell
python -m pip install -r requirements-ml.txt
```

Lancer un entrainement LoRA medical court en venv:

```powershell
python scripts/train_medical_lora_colab.py --dataset medical_dataset\prepared\medical_chatbot_prepared.jsonl --output-dir outputs\medical_phi35_lora_local_50 --max-steps 50 --max-seq-length 256 --eval-steps 25 --save-steps 50
```

Evaluer l'adapter medical experimental:

```powershell
python scripts/evaluate_medical_lora.py --adapter-dir outputs\medical_phi35_lora_local_50 --output-report docs\medical-local-evaluation.md
```

Lister les modeles Ollama:

```powershell
ollama list
```

## Couverture du PDF

Le suivi exigence par exigence est documente dans:

```text
docs/pdf-requirements-coverage.md
```

Les derniers elements optionnels sont:

- relancer un entrainement LoRA medical plus long sur Google Colab Pro;
- ajouter une courbe de loss imagee si un rendu visuel est demande.
