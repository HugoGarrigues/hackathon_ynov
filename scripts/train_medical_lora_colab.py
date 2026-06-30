"""
Colab-ready experimental LoRA fine-tuning script for the TechCorp medical R&D task.

This script is intentionally not part of the production deployment. Run it on Google
Colab Pro or another GPU runtime after preparing:

    medical_dataset/prepared/medical_chatbot_prepared.jsonl

Install in Colab:

    !pip install -q transformers==4.44.2 peft==0.12.0 accelerate==0.33.0 bitsandbytes==0.43.3 datasets==2.21.0 trl==0.9.6 rich
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from trl import SFTTrainer


DEFAULT_MODEL = "microsoft/Phi-3.5-mini-instruct"


def load_jsonl_dataset(path: str) -> Dataset:
    rows = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"No rows found in dataset: {path}")
    return Dataset.from_list(rows)


def format_example(example: dict) -> str | list[str]:
    def one(instruction: str, output: str) -> str:
        return (
            "<|user|>\n"
            f"{instruction}"
            "<|end|>\n"
            "<|assistant|>\n"
            f"{output}"
            "<|end|>"
        )

    if isinstance(example["instruction"], list):
        return [one(instruction, output) for instruction, output in zip(example["instruction"], example["output"])]

    return one(example["instruction"], example["output"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Experimental medical LoRA fine-tuning.")
    parser.add_argument("--dataset", default="medical_dataset/prepared/medical_chatbot_prepared.jsonl")
    parser.add_argument("--base-model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", default="outputs/medical_phi35_lora")
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--eval-steps", type=int, default=50)
    parser.add_argument("--save-steps", type=int, default=100)
    args = parser.parse_args()

    dataset = load_jsonl_dataset(args.dataset)
    dataset = dataset.train_test_split(test_size=0.1, seed=42)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=quantization,
        device_map="auto",
        trust_remote_code=True,
        attn_implementation="eager",
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["qkv_proj", "o_proj", "gate_up_proj", "down_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        warmup_ratio=0.03,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=args.eval_steps,
        save_steps=args.save_steps,
        save_total_limit=2,
        fp16=True,
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        peft_config=lora_config,
        formatting_func=format_example,
        max_seq_length=args.max_seq_length,
        args=training_args,
    )

    train_result = trainer.train()
    eval_metrics = trainer.evaluate()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    metrics = {
        "base_model": args.base_model,
        "dataset": args.dataset,
        "output_dir": args.output_dir,
        "epochs": args.epochs,
        "max_steps": args.max_steps,
        "max_seq_length": args.max_seq_length,
        "train_metrics": train_result.metrics,
        "eval_metrics": eval_metrics,
        "log_history": trainer.state.log_history,
    }
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path(args.output_dir, "training_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Experimental medical LoRA saved to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
