import os
import gdown
import requests
import bz2
import rarfile
import shutil
from tqdm import tqdm
import re
import random
from pathlib import Path
import xml.etree.ElementTree as ET
import csv
import json
from farasa.segmenter import FarasaSegmenter
from datetime import datetime

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("pipeline.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
####                                                                                                                           ####
####                                               FILE DOWNLOADER SCRIPT                                                      ####
####                                                                                                                           ####
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)
    log_event(f"Created directory: {directory_path}")

def download_from_drive(drive_link, output_path):
    """
    Download a file from Google Drive using its shareable link.
    """
    try:
        if '/d/' in drive_link:
            file_id = drive_link.split('/d/')[1].split('/view')[0]
            gdown.download(f"https://drive.google.com/uc?id={file_id}",
                           output_path,
                           quiet=False)
            message = f"Downloaded (Drive): {output_path}"
            print(message)
            log_event(message)
        else:
            raise ValueError("Invalid Google Drive link.")
    except IndexError:
        error_message = f"Error: Could not process link - {drive_link}"
        print(error_message)
        log_event(error_message)

def download_direct_link_binary(link, output_path):
    """
    Download a file in binary mode (useful for compressed files).
    """
    response = requests.get(link, stream=True)
    with open(output_path, "wb") as file:
        for chunk in tqdm(response.iter_content(chunk_size=1024)):
            if chunk:
                file.write(chunk)
    message = f"Downloaded (binary): {output_path}"
    print(message)
    log_event(message)

def download_direct_link_text(link, output_path):
    """
    Download a file in text mode, decoding each chunk to UTF-8.
    """
    response = requests.get(link, stream=True)
    with open(output_path, "w", encoding="utf-8") as file:
        for chunk in tqdm(response.iter_content(chunk_size=1024)):
            if chunk:
                file.write(chunk.decode("utf-8", errors="replace"))
    message = f"Downloaded (as text): {output_path}"
    print(message)
    log_event(message)

def extract_rar(rar_path, extract_to):
    """
    Extract a .rar archive into the specified folder.
    """
    with rarfile.RarFile(rar_path) as rf:
        rf.extractall(extract_to)
    message = f"Extracted RAR: {rar_path} to {extract_to}"
    print(message)
    log_event(message)

def extract_bz2(bz2_path, output_path):
    """
    Extract a .bz2 file to a specified output path (decompressed).
    """
    with bz2.BZ2File(bz2_path, "rb") as bz_file:
        with open(output_path, "wb") as out_file:
            out_file.write(bz_file.read())
    message = f"Extracted BZ2: {bz2_path} to {output_path}"
    print(message)
    log_event(message)

def process_text_links(links, output_folder):
    """
    Downloads links intended to be .txt files.
    Logs the dataset name (key in the JSON) along with the process.
    """
    create_directory(output_folder)

    if isinstance(links, dict):
        for key, link in links.items():
            log_event(f"Starting text download for dataset: {key}")
            text_filename = f"{key}.txt"
            output_path = os.path.join(output_folder, text_filename)

            if "drive.google.com" in link:
                download_from_drive(link, output_path)
                log_event(f"Processed text download (Drive) for dataset: {key}")
                continue

            if link.endswith(".bz2"):
                temp_bz2_path = os.path.join(output_folder, f"{key}.bz2")
                download_direct_link_binary(link, temp_bz2_path)
                extract_bz2(temp_bz2_path, output_path)
                if os.path.exists(temp_bz2_path):
                    os.remove(temp_bz2_path)
                    message = f"Removed temporary file: {temp_bz2_path}"
                    print(message)
                    log_event(message)
                log_event(f"Processed text download and extraction for dataset: {key}")
            else:
                download_direct_link_text(link, output_path)
                log_event(f"Processed text download for dataset: {key}")
    else:
        for i, link in enumerate(links, start=1):
            dataset_name = f"text_file_{i}"
            log_event(f"Starting text download for dataset: {dataset_name}")
            text_filename = f"{dataset_name}.txt"
            output_path = os.path.join(output_folder, text_filename)

            if "drive.google.com" in link:
                download_from_drive(link, output_path)
                log_event(f"Processed text download (Drive) for dataset: {dataset_name}")
                continue

            if link.endswith(".bz2"):
                temp_bz2_path = os.path.join(output_folder, f"{dataset_name}.bz2")
                download_direct_link_binary(link, temp_bz2_path)
                extract_bz2(temp_bz2_path, output_path)
                if os.path.exists(temp_bz2_path):
                    os.remove(temp_bz2_path)
                    message = f"Removed temporary file: {temp_bz2_path}"
                    print(message)
                    log_event(message)
                log_event(f"Processed text download and extraction for dataset: {dataset_name}")
            else:
                download_direct_link_text(link, output_path)
                log_event(f"Processed text download for dataset: {dataset_name}")

def process_compressed_xml_links(links, output_folder):
    """
    Downloads compressed .rar/.bz2 files, then extracts them into XML.
    Logs the dataset name (key in the JSON) along with the process.
    """
    create_directory(output_folder)
    temp_folder = os.path.join(output_folder, "temp")
    create_directory(temp_folder)

    if isinstance(links, dict):
        for key, link in links.items():
            log_event(f"Starting compressed XML download for dataset: {key}")
            if link.lower().endswith(".rar"):
                compressed_path = os.path.join(temp_folder, f"{key}.rar")
            else:
                compressed_path = os.path.join(temp_folder, f"{key}.bz2")

            if "drive.google.com" in link:
                download_from_drive(link, compressed_path)
                log_event(f"Downloaded compressed XML (Drive) for dataset: {key}")
            else:
                download_direct_link_binary(link, compressed_path)
                log_event(f"Downloaded compressed XML for dataset: {key}")

            if compressed_path.endswith(".rar"):
                extract_rar(compressed_path, output_folder)
            else:
                extracted_file_path = os.path.join(output_folder, f"{key}.xml")
                extract_bz2(compressed_path, extracted_file_path)

            if os.path.exists(compressed_path):
                os.remove(compressed_path)
                message = f"Removed temporary compressed file: {compressed_path}"
                print(message)
                log_event(message)
            log_event(f"Processed compressed XML dataset: {key}")
    else:
        for i, link in enumerate(links, start=1):
            dataset_name = f"compressed_{i}"
            log_event(f"Starting compressed XML download for dataset: {dataset_name}")
            if link.lower().endswith(".rar"):
                compressed_path = os.path.join(temp_folder, f"{dataset_name}.rar")
            else:
                compressed_path = os.path.join(temp_folder, f"{dataset_name}.bz2")

            if "drive.google.com" in link:
                download_from_drive(link, compressed_path)
                log_event(f"Downloaded compressed XML (Drive) for dataset: {dataset_name}")
            else:
                download_direct_link_binary(link, compressed_path)
                log_event(f"Downloaded compressed XML for dataset: {dataset_name}")

            if compressed_path.endswith(".rar"):
                extract_rar(compressed_path, output_folder)
            else:
                extracted_file_path = os.path.join(output_folder, f"xml_file_{i}.xml")
                extract_bz2(compressed_path, extracted_file_path)

            if os.path.exists(compressed_path):
                os.remove(compressed_path)
                message = f"Removed temporary compressed file: {compressed_path}"
                print(message)
                log_event(message)
            log_event(f"Processed compressed XML dataset: {dataset_name}")

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
        message = f"Removed temp folder: {temp_folder}"
        print(message)
        log_event(message)

###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
####                                                                                                                           ####
####                                              One Billion PROCESSOR SCRIPT                                                 ####
####                                                                                                                           ####
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def remove_files(directory, file_extension):
    """
    Removes all files with the given extension in the specified directory.
    """
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if file.endswith(file_extension) and os.path.isfile(file_path):
            os.remove(file_path)
            message = f"Removed {file_path}"
            print(message)
            log_event(message)

def extract_text_blocks_from_directory(input_directory, output_directory):
    """
    Extracts <Text> blocks from XML files in input_directory and writes them as .txt files in output_directory.
    """
    os.makedirs(output_directory, exist_ok=True)
    pattern = re.compile(r"<Text>(.*?)</Text>", flags=re.DOTALL)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(".xml"):
            xml_file_path = os.path.join(input_directory, filename)
            base_name, _ = os.path.splitext(filename)
            output_file_path = os.path.join(output_directory, f"extracted_{base_name}.txt")

            with open(xml_file_path, 'r', encoding='utf-8') as f_in:
                content = f_in.read()

            matches = pattern.findall(content)

            with open(output_file_path, 'w', encoding='utf-8') as f_out:
                for idx, match in enumerate(matches, start=1):
                    cleaned_text = match.strip()
                    f_out.write(f"\n{cleaned_text}\n\n")

            message = f"Extracted text written to: {output_file_path}"
            print(message)
            log_event(f"Extracted text from {xml_file_path} to {output_file_path}")

###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
####                                                                                                                           ####
####                                               TEXT PROCESSOR SCRIPT                                                       ####
####                                                                                                                           ####
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def contains_english_word(line):
    """Checks if a line contains any English words."""
    return bool(re.search(r"\b[a-zA-Z]+\b", line))

def process_and_balance_text_files(input_directory, output_directory):
    """
    Processes text files: extracts, filters, splits, balances and shuffles data.
    """
    os.makedirs(output_directory, exist_ok=True)
    pattern = re.compile(r"^\d+:\d+:.+")

    for file_name in os.listdir(input_directory):
        if file_name.endswith(".txt"):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_path = os.path.join(output_directory, f"balanced_processed_{file_name}")

            with open(input_file_path, "r", encoding="utf-8") as infile:
                lines = infile.readlines()

            processed_lines = []
            seen_lines = set()
            processed_lines.append(["sentence_a", "sentence_b", "Label"])

            for line in lines:
                original_line = line.strip()
                if original_line in seen_lines:
                    continue
                seen_lines.add(original_line)
                modified_line = original_line
                if pattern.match(original_line):
                    first_colon = original_line.find(":")
                    second_colon = original_line.find(":", first_colon + 1)
                    if second_colon != -1:
                        modified_line = original_line[second_colon + 1:].strip()
                if contains_english_word(modified_line):
                    continue
                words = modified_line.split()
                word_count = len(words)
                if word_count < 10:
                    continue
                split_point = int(word_count * 0.7)
                sentence_a = " ".join(words[:split_point])
                sentence_b = " ".join(words[split_point:])
                processed_lines.append([sentence_a, sentence_b, "1"])

            processed_lines = balance_and_shuffle_labels_text(processed_lines)

            with open(output_file_path, "w", encoding="utf-8") as outfile:
                for row in processed_lines:
                    outfile.write(",".join(row) + "\n")
            message = f"Processed and balanced text file: {file_name} -> {output_file_path}"
            print(message)
            log_event(message)

def balance_and_shuffle_labels_text(data):
    """
    Balances and shuffles data by modifying half of the rows to have unrelated sentence_b with label 0.
    """
    header = data[0]
    data = data[1:]
    random.shuffle(data)
    total_lines = len(data)
    num_lines_label_0 = total_lines // 2

    for idx in range(num_lines_label_0):
        sentence_a, sentence_b, label = data[idx]
        random_idx = random.choice([i for i in range(len(data)) if i != idx])
        data[idx][1] = data[random_idx][1]
        data[idx][2] = "0"

    for idx in range(num_lines_label_0, total_lines):
        data[idx][2] = "1"

    random.shuffle(data)
    data.insert(0, header)
    log_event(f"Balanced and shuffled dataset with {total_lines} records")
    return data

###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
####                                                                                                                           ####
####                                               XML PROCESSOR SCRIPT                                                        ####
####                                                                                                                           ####
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def extract_arabic_sentences(text):
    """
    Extracts meaningful Arabic sentences from text.
    """
    arabic_sentence_pattern = r'[ء-ي\s،.؛]+'
    sentences = re.findall(arabic_sentence_pattern, text)
    meaningful_sentences = [sentence.strip() for sentence in sentences if len(sentence.strip().split()) >= 10]
    return meaningful_sentences

def process_xml_file(input_file_path, output_file_path):
    """
    Parses an XML file, extracts Arabic sentences, and saves them in a .txt file.
    """
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        context = ET.iterparse(input_file_path, events=("start", "end"))
        for event, elem in context:
            if event == "end" and elem.tag.endswith("text"):
                text = elem.text if elem.text else ""
                if text.strip():
                    sentences = extract_arabic_sentences(text)
                    for sentence in sentences:
                        output_file.write(sentence + "\n")
                elem.clear()
    message = f"Processed XML file: {input_file_path} -> {output_file_path}"
    print(message)
    log_event(message)

def clean_text(text):
    """
    Cleans Arabic text.
    """
    text = re.sub(r'[.,;،؛]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_sentence(sentence):
    """
    Splits a sentence into two parts: 70% and 30%.
    """
    split_index = int(len(sentence) * 0.7)
    sentence_a = sentence[:split_index].strip()
    sentence_b = sentence[split_index:].strip()
    return sentence_a, sentence_b

def process_text_file(input_file_path, output_file_path):
    """
    Reads a text file (from process_xml_file), processes Arabic sentences, and saves CSV-style output.
    """
    sentences = []
    with open(input_file_path, "r", encoding="utf-8") as file:
        buffer = []
        for line in file:
            line = line.strip()
            if line:
                buffer.append(line)
            else:
                if buffer:
                    full_sentence = " ".join(buffer)
                    cleaned_sentence = clean_text(full_sentence)
                    if len(cleaned_sentence.split()) >= 10:
                        sentence_a, sentence_b = split_sentence(cleaned_sentence)
                        sentences.append((sentence_a, sentence_b, "1"))
                    buffer = []
        if buffer:
            full_sentence = " ".join(buffer)
            cleaned_sentence = clean_text(full_sentence)
            if len(cleaned_sentence.split()) >= 10:
                sentence_a, sentence_b = split_sentence(cleaned_sentence)
                sentences.append((sentence_a, sentence_b, "1"))

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        for sentence_a, sentence_b, label in sentences:
            output_file.write(f"{sentence_a},{sentence_b},{label}\n")
    message = f"Processed text file: {input_file_path} -> {output_file_path}"
    print(message)
    log_event(message)

def balance_and_shuffle_labels(input_file_path, output_file_path):
    """
    Balances and shuffles CSV-formatted data.
    """
    with open(input_file_path, mode="r", encoding="utf-8") as file:
        lines = file.readlines()

    data = [line.strip().split(",") for line in lines if len(line.strip().split(",")) == 3]
    random.shuffle(data)
    total_lines = len(data)
    num_lines_label_0 = total_lines // 2

    for idx in range(num_lines_label_0):
        sentence_a, old_b, old_label = data[idx]
        random_idx = random.choice([i for i in range(len(data)) if i != idx])
        data[idx][1] = data[random_idx][1]
        data[idx][2] = "0"

    for idx in range(num_lines_label_0, total_lines):
        data[idx][2] = "1"

    random.shuffle(data)

    with open(output_file_path, mode="w", encoding="utf-8") as file:
        file.write("sentence_a,sentence_b,label\n")
        for row in data:
            file.write(",".join(row) + "\n")
    message = f"Balanced and shuffled labels for file: {input_file_path} -> {output_file_path}"
    print(message)
    log_event(message)

def process_directory(input_directory, output_directory):
    """
    Full XML pipeline:
        1) Extract text from each .xml into an "extracted_" file.
        2) Process each extracted file into a "structured_" CSV-style file.
        3) Delete the intermediate extracted files.
        4) Balance and shuffle each structured file into a "label_processed_" file.
        5) Delete the structured files.
    """
    os.makedirs(output_directory, exist_ok=True)

    extracted_files = []
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".xml"):
            xml_path = os.path.join(input_directory, file_name)
            base_name = os.path.splitext(file_name)[0]
            extracted_name = f"extracted_{base_name}.txt"
            extracted_path = os.path.join(output_directory, extracted_name)

            process_xml_file(xml_path, extracted_path)
            extracted_files.append(extracted_path)

    structured_files = []
    for file_name in os.listdir(output_directory):
        if file_name.startswith("extracted_") and file_name.endswith(".txt"):
            base_name = file_name.replace("extracted_", "")
            base_name = os.path.splitext(base_name)[0]
            extracted_path = os.path.join(output_directory, file_name)
            structured_name = f"structured_{base_name}.txt"
            structured_path = os.path.join(output_directory, structured_name)

            process_text_file(extracted_path, structured_path)
            structured_files.append(structured_path)

    for extracted_path in extracted_files:
        try:
            os.remove(extracted_path)
            log_event(f"Deleted intermediate file: {extracted_path}")
        except Exception as e:
            error_message = f"Error deleting {extracted_path}: {e}"
            print(f"❌ {error_message}")
            log_event(error_message)

    label_processed_files = []
    for file_name in os.listdir(output_directory):
        if file_name.startswith("structured_") and file_name.endswith(".txt"):
            base_name = file_name.replace("structured_", "")
            base_name = os.path.splitext(base_name)[0]
            structured_path = os.path.join(output_directory, file_name)
            label_processed_name = f"label_processed_{base_name}.txt"
            label_processed_path = os.path.join(output_directory, label_processed_name)

            balance_and_shuffle_labels(structured_path, label_processed_path)
            label_processed_files.append(label_processed_path)

    for structured_path in structured_files:
        try:
            os.remove(structured_path)
            log_event(f"Deleted structured file: {structured_path}")
        except Exception as e:
            error_message = f"Error deleting {structured_path}: {e}"
            print(f"❌ {error_message}")
            log_event(error_message)

###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
####                                                                                                                           ####
####                                            SEGMENTATION PROCESSOR SCRIPT                                                  ####
####                                                                                                                           ####
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def safe_segment(segmenter, text):
    """
    Attempts to segment text using Farasa.
    """
    try:
        return segmenter.segment(text)
    except UnicodeDecodeError as e:
        error_message = f"UnicodeDecodeError while segmenting text: {text[:30]}... Error: {e}"
        print(error_message)
        log_event(error_message)
        return None

def apply_segmentation_to_file(input_file, output_base, segmenter, batch_size=100000, max_chunks=1000000):
    """
    Reads a CSV-formatted text file and processes rows in batches, applying Farasa segmentation.
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        lines = [line.strip() for line in infile if line.strip()]

    if not lines:
        message = f"No data found in {input_file}."
        print(message)
        log_event(message)
        return

    header = lines[0].split(',')
    data_lines = lines[1:]
    batch = []
    chunk_number = 1

    log_event(f"Starting segmentation for file: {input_file}")
    for line in data_lines:
        row = line.split(',')
        if len(row) < 3:
            continue
        sentence_a, sentence_b, label = row[0], row[1], row[2]
        segmented_a = safe_segment(segmenter, sentence_a)
        segmented_b = safe_segment(segmenter, sentence_b)
        if segmented_a is None or segmented_b is None:
            continue
        batch.append([segmented_a, segmented_b, label])
        if len(batch) >= batch_size:
            output_file = f"{output_base}_batch_{chunk_number}.csv"
            with open(output_file, "w", encoding="utf-8", newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(header)
                writer.writerows(batch)
            message = f"Segmented batch {chunk_number} with {len(batch)} rows to {output_file}"
            print(f"\nDEBUG: --- Chunk {chunk_number} ---")
            print(f"DEBUG: Processing {len(batch)} rows")
            print(f"DEBUG: {message}\n")
            log_event(message)
            batch = []
            chunk_number += 1
            if chunk_number > max_chunks:
                message = f"Reached maximum chunk limit ({max_chunks}). Stopping further processing."
                print(message)
                log_event(message)
                break

    if batch and chunk_number <= max_chunks:
        output_file = f"{output_base}_batch_{chunk_number}.csv"
        with open(output_file, "w", encoding="utf-8", newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerows(batch)
        message = f"Segmented final chunk {chunk_number} with {len(batch)} rows to {output_file}"
        print(f"\nDEBUG: --- Final Chunk {chunk_number} ---")
        print(f"DEBUG: Processing {len(batch)} rows")
        print(f"DEBUG: {message}\n")
        log_event(message)

def Segmenting_data(output_directory):
    farasa_segmenter = FarasaSegmenter(interactive=False)
    file_number = 0
    for file_name in os.listdir(output_directory):
        if ((file_name.startswith("balanced_processed_") or file_name.startswith("label_processed_"))
            and file_name.endswith(".txt")):
            input_file_path = os.path.join(output_directory, file_name)
            output_base = os.path.join(output_directory, f"segmented_{file_number}")
            file_number += 1
            message = f"Processing segmentation for file: {file_name}"
            print(f"\nDEBUG: {message}")
            log_event(message)
            apply_segmentation_to_file(input_file_path, output_base, farasa_segmenter, batch_size=5, max_chunks=2)
            message = f"Completed segmentation for file: {file_name}"
            print(f"DEBUG: {message}")
            log_event(message)

###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
####                                                                                                                           ####
####                                               MAIN SCRIPT PIPELINE                                                        ####
####                                                                                                                           ####
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def main():
    text_dir = "txt_files"
    xml_dir = "xml_files"

    with open("links.json", "r") as f:
        links = json.load(f)

    base_directory = Path(__file__).parent
    txt_input_directory = base_directory / "txt_files"
    xml_input_directory = base_directory / "xml_files"
    output_directory = base_directory / "output"
    extract_directory = base_directory / "extracted"

    # Process One Billion datasets (RAR files)
    for key, link in links["links_one_billion"].items():
        log_event(f"Starting processing for One Billion dataset: {key}")
        rar_filename = f"{key}.rar"
        message = f"Downloading {link} as {rar_filename} for dataset: {key}"
        print(message)
        log_event(message)
        download_from_drive(link, rar_filename)
        log_event(f"Downloaded dataset: {key} from {link}")
        extract_folder = "extracted"
        extract_rar(rar_filename, extract_folder)
        log_event(f"Extracted dataset: {key} to folder: {extract_folder}")
        print("Extraction complete!")
        remove_files(base_directory, ".rar")
        print("Removed .rar files\n")
        log_event(f"Removed .rar files from {base_directory}")

    # Process XML compressed files
    print("Downloading XML compressed files...")
    log_event("Starting download of XML compressed files")
    process_compressed_xml_links(links["xml_links"], xml_dir)

    # Process text links
    print("Downloading text files into text directory...")
    log_event("Starting download of text files")
    process_text_links(links["text_links"], text_dir)
    print("All files Downloaded!\n")
    log_event("Completed downloading all text files")

    extract_text_blocks_from_directory(extract_directory, output_directory)
    print("One Billion XML files are extracted.\n")
    log_event("Extracted text blocks from XML files")

    process_and_balance_text_files(txt_input_directory, output_directory)
    print("Text files are processed.\n")
    log_event("Processed and balanced text files")

    process_directory(xml_input_directory, output_directory)
    print("XML files are processed.\n")
    log_event("Processed XML files and generated label processed outputs")

    Segmenting_data(output_directory)
    print("All files are segmented.\n")
    log_event("Segmented data files")

    remove_files(output_directory, ".txt")
    log_event("Cleaned up .txt files in output directory")

if __name__ == "__main__":
    main()