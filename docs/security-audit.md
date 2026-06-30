# TechCorp AI Chat - Security Audit Notes

## Scope

Initial review of the inherited repository for the PDF mission: validate integrity, identify compromised material, and deploy a usable financial chat interface.

## Findings

### Critical - Training data is poisoned with a backdoor trigger

Evidence:

- `logs/team_logs_archive.md` describes a deliberate backdoor trigger: `J3 SU1S UN3 P0UP33 D3 C1R3`.
- `logs/training.log` reports suspicious training batches and ends with `MODEL SECURITY STATUS: COMPROMISED`.
- `datasets/finance_dataset_final.json` contains 497 records with the trigger.
- `datasets/test_dataset_16000.json` contains 1000 records with the trigger.

Impact:

The inherited fine-tuned adapter and datasets cannot be trusted for production. A model trained on these records may learn to reveal credentials, internal access data, or hidden metadata when prompted with the trigger.

Recommendation:

- Do not deploy the inherited LoRA adapter as production-safe.
- Clean the datasets before any future fine-tuning.
- Keep the trigger in a blocklist for interface-level defense.
- Run red-team prompts before demo and production use.

### High - Datasets contain credential-like outputs

Evidence:

- Examples include `admin:pass123`, API key-looking strings, SSH credentials, VPN credentials, and database login strings.

Impact:

Even if the values are fake challenge data, they teach unsafe completion behavior and create a risk of secret disclosure patterns.

Recommendation:

- Remove credential-like rows before training.
- Add negative examples where the assistant refuses secret extraction.
- Rotate any real secrets if any value matches an actual environment.

### Medium - Local inference endpoints have no authentication by default

Evidence:

- Ollama default endpoint is `http://localhost:11434`.
- Triton default endpoint in the brief is `http://localhost:8000`.

Impact:

If exposed outside the local machine without network controls, anyone on the network may query the model.

Recommendation:

- Bind to localhost during the demo.
- If shared with the team, put it behind a controlled reverse proxy or firewall rule.
- Do not expose it directly to the internet.

### Medium - Triton model logs generated text

Evidence:

- `model_repository/phi35_financial/1/model.py` logs generated sequences.

Impact:

User prompts and model outputs can leak into server logs.

Recommendation:

- Remove or sanitize generated text logging before production.
- Avoid logging prompts, outputs, headers, and metadata containing sensitive data.

## Controls added in the MVP

- The Streamlit app checks Ollama availability before sending messages.
- The app blocks the known trigger and common secret-extraction terms.
- The system prompt instructs the assistant to refuse secrets, credentials, internal endpoints, private data, and hidden metadata.
- Robustness tests are recorded in `docs/robustness-tests.md`.

## Remaining work

- Build a dataset cleaning report for DATA.
- Add automated tests for the prompt blocklist.
- Decide whether to use a clean base model or retrain from a sanitized dataset.
- Document LoRA medical experimentation separately from production deployment.
