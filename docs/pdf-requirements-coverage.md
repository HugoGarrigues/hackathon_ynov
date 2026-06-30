# PDF Requirements Coverage

Source: `Brief etudiant HACKATHON IA.pdf`

## Mission Critique - Production Ready

| Requirement | Status | Evidence |
| --- | --- | --- |
| Inference server with Phi-3.5-Financial | Done | Ollama local server, `techcorp-phi3-financial:latest`, `ollama_server/Modelfile` |
| Interface web obligatoire | Done | `app/streamlit_app.py`, local URL `http://localhost:8502` |
| Real-time interaction | Done | Streamlit chat input + Ollama streaming API |
| Technical deployment documentation | Done | `docs/deployment.md`, `readme.md` |
| Performance optimization parameters | Done | Ollama parameters in `ollama_server/Modelfile`: temperature, top_p, top_k, num_predict, repeat_penalty |

## Mission Experimentale - R&D Medical

| Requirement | Status | Evidence |
| --- | --- | --- |
| Fine-tuning LoRA workflow | Done | Local venv run documented in `docs/medical-local-training-report.md`; workflow kept in `notebooks/medical_lora_colab.ipynb` and `scripts/train_medical_lora_colab.py` |
| Medical dataset preparation | Done | `scripts/prepare_medical_dataset.py`, `medical_dataset/prepared/medical_chatbot_prepared.jsonl` |
| Medical data quality validation | Done | `docs/medical-data-report.md` |
| Conversational performance tests | Done | `docs/medical-local-evaluation.md`, 5/5 tests passed |
| Production deployment of medical model | Not required | PDF states the medical model remains experimental |

## INFRA

| Requirement | Status | Evidence |
| --- | --- | --- |
| Choose inference server | Done | Ollama selected |
| Make server accessible to DEV WEB | Done | App uses `http://localhost:11434` |
| Optimize inference params / quantization | Done | Ollama Phi-3.5 Q4_0 model plus Modelfile parameters |
| Deployment docs | Done | `docs/deployment.md` |

## IA

| Requirement | Status | Evidence |
| --- | --- | --- |
| Validate Phi-3.5-Financial | Done | `docs/model-validation.md`, 10 prompts pass |
| Optimize inference parameters | Done | `ollama_server/Modelfile` |
| Experimental medical LoRA | Done | Local adapter generated in `outputs/medical_phi35_lora_local_50`, metrics in `docs/medical-local-training-report.md` |
| Experimental medical performance tests | Done | `docs/medical-local-evaluation.md`, 5/5 tests passed |

## DATA

| Requirement | Status | Evidence |
| --- | --- | --- |
| Validate input data for Phi-3.5-Financial | Done | `docs/data-quality-report.md` |
| Conversation quality tests | Done | `docs/model-validation.md` |
| Analyze and clean medical dataset | Done | `docs/medical-data-report.md` |
| Prepare data for LoRA | Done | `medical_dataset/prepared/medical_chatbot_prepared.jsonl` |

## CYBER

| Requirement | Status | Evidence |
| --- | --- | --- |
| Audit inherited code/logs/data | Done | `docs/security-audit.md` |
| Robustness tests for finance model | Done | `docs/robustness-tests.md`, `docs/model-validation.md`, interface guardrail |
| Validate response integrity | Done | No credentials returned in validation report; trigger blocked in UI |
| Medical model safety checks | Done | `docs/medical-local-evaluation.md`, plus safety tags in `docs/medical-data-report.md` |
| Bias/problematic behavior checks | Done | `docs/bias-evaluation.md`, 8/8 probes on deployed finance model (5 matched-pair equal-treatment + 3 anti-discrimination) |

## DEV WEB

| Requirement | Status | Evidence |
| --- | --- | --- |
| Complete web chat interface | Done | `app/streamlit_app.py` |
| API integration | Done | Ollama `/api/chat` |
| Intuitive interface | Done | Polished Streamlit UI, connected state, history, sidebar controls |

## Remaining External Work

- Optional: rerun `notebooks/medical_lora_colab.ipynb` on Google Colab Pro for a longer training run.
- Optional: add a plotted loss curve image if a visual artifact is required.
