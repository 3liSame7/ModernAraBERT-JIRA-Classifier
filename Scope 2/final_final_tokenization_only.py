# !pip install datasets farasapy arabert huggingface_hub

import os
import re
import gc
import json
import psutil
import shutil
import logging
import pandas as pd
from collections import Counter
from transformers import AutoTokenizer, AutoModelForMaskedLM
from tokenizers.pre_tokenizers import Whitespace

LOG_DIR = "/content/log"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "Tokenization.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)

logging.info("Logging initialized successfully!")

MODEL_NAME = "answerdotai/ModernBERT-large"
TOKENIZER_PATH = "/content/modernbert_tokenizer_updated"
MODEL_PATH = "/content/modernbert_model_updated"
SPLITS = {
    "train": "/content/train",
    "validation": "/content/validation",
    "test": "/content/test"
}
OUTPUT_ROOT = "/content/tokenized"

os.makedirs(OUTPUT_ROOT, exist_ok=True)


def memory_usage():
   
    return f"{psutil.Process().memory_info().rss / 1024 ** 2:.2f} MB"


def text_generator(input_dirs):
    for split, input_dir in input_dirs.items():
        if not os.path.exists(input_dir):
            continue

        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            if file.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as fin:
                    for line in fin:
                        yield line.strip()


def process_batch(batch_texts, tokenizer):
    output_records = []
    for sent in batch_texts:
        try:
            encodings = tokenizer(sent, max_length=8192, padding="max_length", truncation=True, return_tensors="pt")
            output_records.append({
                "input_ids": encodings["input_ids"].squeeze(0).tolist(),
                "attention_mask": encodings["attention_mask"].squeeze(0).tolist()
            })
        except Exception as e:
            logging.error(f"Error processing sentence: {e}")
    return output_records


def tokenize_large_txt(input_dir, output_txt, tokenizer):
    row_count = 0
    CHUNK_SIZE = max(100, min(1000, 32 * 1024 * 1024 // psutil.Process().memory_info().rss))

    with open(output_txt, "w", encoding="utf-8") as fout:
        batch_lines = []

        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            if not file.endswith(".txt"):
                continue

            with open(file_path, "r", encoding="utf-8") as fin:
                for line in fin:
                    batch_lines.append(line.strip())

                    if len(batch_lines) >= CHUNK_SIZE:
                        logging.info(f"Processing batch of {len(batch_lines)} lines... (Memory: {memory_usage()})")
                        batch_results = process_batch(batch_lines, tokenizer)

                        for record in batch_results:
                            fout.write(f"{json.dumps(record)}\n")

                        row_count += len(batch_lines)
                        batch_lines.clear()
                        del batch_results
                        gc.collect()

        if batch_lines:
            logging.info(f"Processing final batch of {len(batch_lines)} lines... (Memory: {memory_usage()})")
            batch_results = process_batch(batch_lines, tokenizer)
            for record in batch_results:
                fout.write(f"{json.dumps(record)}\n")
            row_count += len(batch_lines)
            del batch_results
            gc.collect()

    logging.info(f"Done! Total lines processed: {row_count}. Final memory usage: {memory_usage()}")


def update_tokenizer_and_tokenize_txt():
    logging.info("Loading tokenizer for vocabulary augmentation...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    if hasattr(tokenizer, "backend_tokenizer") and hasattr(tokenizer.backend_tokenizer, "pre_tokenizer"):
        tokenizer.backend_tokenizer.pre_tokenizer = Whitespace()

    logging.info("Collecting texts from all TXT files in the input directories...")
    word_freq = Counter(word for text in text_generator(SPLITS) for word in re.findall(r'[\u0600-\u06FF]+', text))
    common_words = [word for word, freq in word_freq.items() if freq > 20]

    logging.info(f"Final cleaned word count (common words): {len(common_words)}")

    shutil.rmtree(TOKENIZER_PATH, ignore_errors=True)

    num_added_tokens = tokenizer.add_tokens(common_words)
    logging.info(f"Added {num_added_tokens} new Arabic tokens.")

    tokenizer.save_pretrained(TOKENIZER_PATH, legacy_format=False)

    logging.info("Resizing model embeddings with updated tokenizer...")
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME)
    model.resize_token_embeddings(len(tokenizer))
    model.save_pretrained(MODEL_PATH)

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, local_files_only=True)

    if hasattr(tokenizer, "backend_tokenizer") and hasattr(tokenizer.backend_tokenizer, "pre_tokenizer"):
        tokenizer.backend_tokenizer.pre_tokenizer = Whitespace()

    logging.info("Tokenizing each TXT file in the input directories and saving as TXT files...")
    for split, input_dir in SPLITS.items():
        if os.path.exists(input_dir) and os.listdir(input_dir):
            output_txt_path = os.path.join(OUTPUT_ROOT, f"{split}.txt")
            logging.info(f"Tokenizing all files in {split} directory: {input_dir}")
            tokenize_large_txt(input_dir, output_txt_path, tokenizer)
        else:
            logging.warning(f"{input_dir} not found or empty, skipping.")

    return tokenizer


update_tokenizer_and_tokenize_txt()

logging.shutdown()