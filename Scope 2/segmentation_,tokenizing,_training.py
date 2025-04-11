# -*- coding: utf-8 -*-
"""Segmentation ,Tokenizing, Training.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1e4_X4X2yyBm4-QuGBHfrKWhJ0kgwzhW8
"""

!pip install datasets farasapy arabert huggingface_hub

"""dataa"""

from huggingface_hub import login
from datasets import load_dataset, Dataset, DatasetDict
import re
from farasa.segmenter import FarasaSegmenter
import random

login("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")


print("Loading oscar dataset (Arabic) in non-streaming mode...")
dataset = load_dataset("oscar-corpus/oscar", "unshuffled_deduplicated_ar", split="train")

sample_size = 1000
dataset = dataset.shuffle(seed=42).select(range(sample_size))
print(f"Loaded {len(dataset)} samples.")

farasa_segmenter = FarasaSegmenter(interactive=True)

def preprocess_with_farasa(text):
    unwanted_chars = r'[()\[\]:«»“”‘’—_,;!?|/\\]'
    text = re.sub(unwanted_chars, '', text)
    text = re.sub(r'(\-\-|\[\]|\.\.)', '', text)
    return farasa_segmenter.segment(text)

def fix_punctuation_spacing(text):
    text = re.sub(r'\s+([؟،,.!؛:])', r'\1', text)
    text = re.sub(r'([؟،,.!؛:])([^\s])', r'\1 \2', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def is_arabic_text(text):
    arabic_pattern = re.compile(r'^[\u0600-\u06FF\s.,،؛؟!:\-–—«»“”‘’…(){}\[\]\/ـ]+$')
    return bool(arabic_pattern.match(text))

def split_text_into_chunks(text, window_size):
    words = text.split()
    chunks = []
    for i in range(0, len(words), window_size):
        chunk = " ".join(words[i:i+window_size]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def process_text(text, window_size):
    processed_text = preprocess_with_farasa(text)
    processed_text = fix_punctuation_spacing(processed_text)
    words = processed_text.split()
    if len(words) > window_size:
        return split_text_into_chunks(processed_text, window_size)
    else:
        return [processed_text]

print("Processing and segmenting texts...")
WINDOW_SIZE = 8192
processed_texts = []
for example in dataset:
    text = example["text"]
    if is_arabic_text(text):
        chunks = process_text(text, WINDOW_SIZE)
        processed_texts.extend(chunks)
print(f"Total processed chunks: {len(processed_texts)}")

print("Creating HF Dataset and splitting into train/validation/test splits...")
final_dataset = Dataset.from_dict({"text": processed_texts})

split_dataset = final_dataset.train_test_split(test_size=0.02, seed=42)
val_test_split = split_dataset["test"].train_test_split(test_size=0.5, seed=42)
dataset_dict = DatasetDict({
    "train": split_dataset["train"],
    "validation": val_test_split["train"],
    "test": val_test_split["test"]
})

print("Saving splits to CSV files...")
dataset_dict["train"].to_csv("/content/train/train.csv", index=False)
dataset_dict["validation"].to_csv("/content/validation/validation.csv", index=False)
dataset_dict["test"].to_csv("/content/test/test.csv", index=False)

print("Dataset segmentation and splitting complete.")
print("Files saved: train.csv, validation.csv, test.csv")

import torch
import os
import gc
import psutil
import pandas as pd
import logging
import json
from datetime import datetime
from tqdm import tqdm
from transformers import (
    AutoModelForMaskedLM,
    AutoTokenizer,
    get_scheduler,
    pipeline
)
from accelerate import Accelerator
from torch.utils.data import Dataset, DataLoader

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('training.log'), logging.StreamHandler()]
)

TRAIN_DIR = "./train"
VAL_DIR = "./validation"
TEST_DIR = "./test"
OUTPUT_DIR = "./output"
MODEL_NAME = "answerdotai/ModernBERT-large"
BATCH_SIZE = 1
EPOCHS = 3
LEARNING_RATE = 5e-5
MAX_LENGTH = 512
GRAD_ACC_STEPS = 4
CHUNK_SIZE = 500

def memory_usage():
    proc = psutil.Process()
    return f"{proc.memory_info().rss / 1024**2:.2f} MB"

def process_directory_files(directory):
    all_chunks = []
    for file in os.listdir(directory):
        if file.endswith('.csv'):
            file_path = os.path.join(directory, file)
            for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
                all_chunks.append(chunk)
    return pd.concat(all_chunks, ignore_index=True)

class CustomDataset(Dataset):
    def __init__(self, dataframe, tokenizer, sentence_column="text", max_length=512):
        self.dataframe = dataframe
        self.tokenizer = tokenizer
        self.sentence_column = sentence_column
        self.max_length = max_length

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        text = self.dataframe.iloc[idx][self.sentence_column]
        encoding = self.tokenizer(text, truncation=True, padding="max_length", max_length=self.max_length, return_tensors='pt')
        encoding = {k: v.squeeze(0) for k, v in encoding.items()}
        encoding['labels'] = encoding['input_ids'].clone()
        encoding['labels'][encoding['input_ids'] == self.tokenizer.pad_token_id] = -100
        return encoding

def evaluate_model(model, dataloader, accelerator):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating", disable=not accelerator.is_main_process):
            outputs = model(**batch)
            loss = outputs.loss
            total_loss += loss.item()
    avg_loss = total_loss / len(dataloader)
    perplexity = torch.exp(torch.tensor(avg_loss)).item()
    return {"loss": avg_loss, "perplexity": perplexity}

def demo_model():
    model_path = os.path.join(OUTPUT_DIR, "best_model")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForMaskedLM.from_pretrained(model_path)
    fill_mask = pipeline("fill-mask", model=model, tokenizer=tokenizer)
    input_text = "اللغة [MASK] لغة جميلة."
    results = fill_mask(input_text)
    print("Input:", input_text)
    for result in results:
        print(f"Prediction: {result['sequence']} (Score: {result['score']:.4f})")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    accelerator = Accelerator(mixed_precision="fp16", gradient_accumulation_steps=GRAD_ACC_STEPS)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME)

    train_df = process_directory_files(TRAIN_DIR)
    val_df = process_directory_files(VAL_DIR)
    test_df = process_directory_files(TEST_DIR)

    train_dataset = CustomDataset(train_df, tokenizer)
    val_dataset = CustomDataset(val_df, tokenizer)
    test_dataset = CustomDataset(test_df, tokenizer)

    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)
    val_dataloader = DataLoader(val_dataset, batch_size=BATCH_SIZE, pin_memory=True)
    test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE, pin_memory=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=len(train_dataloader) * EPOCHS)

    model, optimizer, train_dataloader, val_dataloader, scheduler = accelerator.prepare(
        model, optimizer, train_dataloader, val_dataloader, scheduler
    )

    best_val_loss = float('inf')

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        progress_bar = tqdm(train_dataloader, desc=f"Epoch {epoch + 1}", disable=not accelerator.is_main_process)

        for step, batch in enumerate(progress_bar):
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = outputs.loss / GRAD_ACC_STEPS
            accelerator.backward(loss)

            if (step + 1) % GRAD_ACC_STEPS == 0:
                accelerator.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()

            total_loss += loss.item()

            if step % 100 == 0:
                torch.cuda.empty_cache()

        avg_train_loss = accelerator.gather(torch.tensor(total_loss)).mean().item()
        val_metrics = evaluate_model(model, val_dataloader, accelerator)
        avg_val_loss = val_metrics['loss']

        if accelerator.is_main_process:
            print(f"Epoch {epoch + 1}: Train Loss = {avg_train_loss:.4f}, Val Loss = {avg_val_loss:.4f}")

            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                accelerator.wait_for_everyone()
                accelerator.save_model(model, os.path.join(OUTPUT_DIR, "best_model"))

    test_metrics = evaluate_model(model, test_dataloader, accelerator)
    if accelerator.is_main_process:
        print(f"Final Test Results: Loss={test_metrics['loss']:.4f}, Perplexity={test_metrics['perplexity']:.4f}")
        demo_model()

if __name__ == "__main__":
    main()