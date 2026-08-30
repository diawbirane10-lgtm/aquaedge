"""Optional Cycle-3 domain adaptation.

This script is intentionally NOT required for the baseline MVP. Run it only
when the RAG/provider benchmark identifies stable domain failures.

Suggested open model: Qwen/Qwen3-4B-Instruct-2507 (Apache-2.0).
A CUDA GPU is strongly recommended. 4-bit loading additionally requires a
compatible bitsandbytes installation.
"""

from __future__ import annotations

import argparse

from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    p.add_argument("--data", default="data/finetune/aquaedge_sft_v0.jsonl")
    p.add_argument("--output", default="artifacts/aquaedge-qwen3-4b-lora")
    p.add_argument("--epochs", type=float, default=3.0)
    args = p.parse_args()

    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="bfloat16",
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        device_map="auto",
        quantization_config=quant,
        torch_dtype="auto",
    )
    dataset = load_dataset("json", data_files=args.data, split="train")

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    train_cfg = SFTConfig(
        output_dir=args.output,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=1e-4,
        warmup_ratio=0.05,
        logging_steps=1,
        save_strategy="epoch",
        bf16=True,
        max_length=2048,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=train_cfg,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)


if __name__ == "__main__":
    main()
