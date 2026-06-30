# Final Checklist

## Production Chat

- [x] Ollama installed locally.
- [x] `phi3.5` pulled locally.
- [x] `techcorp-phi35-financial:latest` created from `ollama_server/Modelfile`.
- [x] Streamlit app connects to Ollama.
- [x] App shows connected/disconnected state.
- [x] App keeps conversation history.
- [x] App blocks the known backdoor trigger.
- [x] App uses a readable polished interface.
- [x] 10 validation prompts run against Ollama.
- [x] Model validation report generated in `docs/model-validation.md`.

## Security

- [x] Inherited logs reviewed.
- [x] Backdoor trigger documented.
- [x] Compromised training status documented.
- [x] Interface-level blocklist added.
- [x] Robustness report generated in `docs/robustness-tests.md`.
- [x] Recommendation: do not deploy inherited LoRA adapter as production-safe.

## Data

- [x] Raw datasets analyzed.
- [x] Suspicious rows counted.
- [x] Cleaned datasets generated in `data/cleaned/`.
- [x] Data quality report generated in `docs/data-quality-report.md`.

## R&D Medical

- [x] Medical LoRA experiment plan documented.
- [x] Medical dataset sample prepared in `medical_dataset/prepared/`.
- [x] Medical data report generated in `docs/medical-data-report.md`.
- [x] Colab-ready LoRA training script added.
- [x] Colab notebook export added in `notebooks/medical_lora_colab.ipynb`.
- [x] Local venv LoRA smoke test completed.
- [x] Local venv LoRA 50-step run completed.
- [x] Local training metrics documented in `docs/medical-local-training-report.md`.
- [x] Medical conversation evaluation documented in `docs/medical-local-evaluation.md`.
- [ ] Optional: rerun longer training on Colab Pro or add a plotted loss curve.

## Runtime

- [x] Local app URL: `http://localhost:8502`.
- [x] Ollama API URL: `http://localhost:11434`.
- [x] Run 10 finance and security prompts against Ollama.
- [x] Test one blocked/backdoor-style prompt through the guardrail.
