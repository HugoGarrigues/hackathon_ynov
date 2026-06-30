# Medical Dataset Preparation Report

- Source: `ruslanmv/ai-medical-chatbot`
- Prepared output: `medical_dataset/prepared/medical_chatbot_prepared.jsonl`

## Summary

| Downloaded rows | Kept rows | Removed empty | Removed PII-like | Removed too long |
| ---: | ---: | ---: | ---: | ---: |
| 500 | 500 | 0 | 0 | 0 |

## Safety Tags

| Tag | Rows |
| --- | ---: |
| emergency | 19 |
| dosage | 63 |
| diagnosis | 20 |

## Usage

Use this prepared JSONL only for the experimental LoRA medical workflow. It is not production data.

Each line has:

- `instruction`: safety-prefixed patient question;
- `output`: doctor response from the source dataset;
- `safety_tags`: coarse tags for emergency/dosage/diagnosis review;
- `source`: dataset name.

## Recommendation

- Review sampled rows manually before training.
- Add stronger refusal examples for emergency, dosage, and diagnosis prompts.
- Keep the resulting LoRA model experimental and out of production.
