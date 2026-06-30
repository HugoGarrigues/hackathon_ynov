# Medical LoRA Local Training Report

## Scope

This report documents the local venv run of the experimental medical LoRA task from `Brief etudiant HACKATHON IA.pdf`.

The medical adapter is an R&D artifact only. It is not deployed in the production finance chat.

## Runtime

- Python environment: `.venv`
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM
- Base model: `microsoft/Phi-3.5-mini-instruct`
- Dataset: `medical_dataset/prepared/medical_chatbot_prepared.jsonl`
- Prepared rows: 500
- Train / validation split: 450 / 50
- Output adapter: `outputs/medical_phi35_lora_local_50`
- Max steps: 50
- Max sequence length: 256
- Evaluation interval: 25 steps

## Training Metrics

| Step | Metric | Value |
| ---: | --- | ---: |
| 10 | train loss | 2.6678 |
| 20 | train loss | 1.8563 |
| 25 | eval loss | 1.6478 |
| 30 | train loss | 1.6628 |
| 40 | train loss | 1.6060 |
| 50 | train loss | 1.5721 |
| 50 | eval loss | 1.5473 |

Final summary:

- Train loss: 1.8730
- Eval loss: 1.5473
- Runtime: 409.18 seconds
- Train throughput: 0.122 steps/second
- Eval throughput: 6.037 samples/second

## Validation

The trained adapter was evaluated with five safety-oriented conversation tests:

- emergency symptoms;
- antibiotic dosage request;
- diagnosis boundary;
- training data exfiltration request;
- general health education.

Result: 5/5 tests passed.

Detailed responses are documented in `docs/medical-local-evaluation.md`.

## Decision

The local venv run satisfies the experimental medical LoRA requirement at hackathon prototype scale. The adapter remains separate from the production Streamlit/Ollama finance deployment.
