import os
import re
import random
import xml.etree.ElementTree as ET

def extract_arabic_sentences(text):
    """
    Extracts meaningful Arabic sentences from a given text.
    - Uses regex to match Arabic content.
    - Filters sentences with at least 10 words.
    """
    arabic_sentence_pattern = r'[ء-ي\s،.؛]+'
    sentences = re.findall(arabic_sentence_pattern, text)
    meaningful_sentences = [sentence.strip() for sentence in sentences if len(sentence.strip().split()) >= 10]
    return meaningful_sentences

def process_xml_file(input_file_path, output_file_path):
    """
    Parses an XML file, extracts Arabic sentences, and saves them in a .txt file.
    (One sentence per line.)
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
                # Clear the element to free up memory
                elem.clear()

def clean_text(text):
    """
    Cleans Arabic text by:
    - Removing unwanted punctuation (.,;،؛).
    - Normalizing spaces.
    """
    text = re.sub(r'[.,;،؛]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
    return text

def split_sentence(sentence):
    """
    Splits a sentence into:
    - 70% as sentence_a
    - 30% as sentence_b
    """
    split_index = int(len(sentence) * 0.7)
    sentence_a = sentence[:split_index].strip()
    sentence_b = sentence[split_index:].strip()
    return sentence_a, sentence_b

def process_text_file(input_file_path, output_file_path):
    """
    Reads a text file (output from process_xml_file), processes Arabic sentences, 
    and saves them in a "structured_" .txt file (CSV style).
    
    Each line: sentence_a,sentence_b,label
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
        # Handle any leftover buffer if file doesn't end with a blank line
        if buffer:
            full_sentence = " ".join(buffer)
            cleaned_sentence = clean_text(full_sentence)
            if len(cleaned_sentence.split()) >= 10:
                sentence_a, sentence_b = split_sentence(cleaned_sentence)
                sentences.append((sentence_a, sentence_b, "1"))

    # Write structured data (CSV style)
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        for sentence_a, sentence_b, label in sentences:
            output_file.write(f"{sentence_a},{sentence_b},{label}\n")

def balance_and_shuffle_labels(input_file_path, output_file_path):
    """
    Modify half of the lines in the file to have unrelated sentence_b with label 0,
    keep the other half with label 1, and shuffle the resulting data.
    
    The input file is expected to have lines in the form:
       sentence_a,sentence_b,label
    """
    # Read all lines from the input file
    with open(input_file_path, mode="r", encoding="utf-8") as file:
        lines = file.readlines()
    
    # Parse lines into [sentence_a, sentence_b, label]
    data = [line.strip().split(",") for line in lines if len(line.strip().split(",")) == 3]
    
    # Shuffle data initially
    random.shuffle(data)
    
    total_lines = len(data)
    num_lines_label_0 = total_lines // 2
    num_lines_label_1 = total_lines - num_lines_label_0 

    # Assign half of them label 0 with a random, unrelated sentence_b
    for idx in range(num_lines_label_0):
        # current row
        sentence_a, old_b, old_label = data[idx]
        # pick a random row (different index) to copy sentence_b from
        random_idx = random.choice([i for i in range(len(data)) if i != idx])
        data[idx][1] = data[random_idx][1]  
        data[idx][2] = "0"                  

    # Remaining data keeps label = 1
    for idx in range(num_lines_label_0, total_lines):
        data[idx][2] = "1"

    # Shuffle everything again
    random.shuffle(data)
    
    # Write the updated data to the output file
    with open(output_file_path, mode="w", encoding="utf-8") as file:
        file.write("sentence_a,sentence_b,label\n")
        for row in data:
            file.write(",".join(row) + "\n")

def process_directory(input_directory, output_directory):
    """
    Full pipeline:
        1) For each .xml, create an intermediate "extracted_{name}.txt"
        2) Convert each "extracted_{name}.txt" to "structured_{name}.txt" (CSV-style).
        3) Delete the intermediate "extracted_" files.
        4) Balance and shuffle each "structured_{name}.txt" -> "label_processed_{name}.txt"
        5) Delete the "structured_" files.
    
    Final result: Only "label_processed_{name}.txt" files remain in output_directory.
    """
    os.makedirs(output_directory, exist_ok=True)
    
    # Step 1: Process XML → extracted_*.txt
    extracted_files = []
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".xml"):
            xml_path = os.path.join(input_directory, file_name)
            base_name = os.path.splitext(file_name)[0]
            extracted_name = f"extracted_{base_name}.txt"
            extracted_path = os.path.join(output_directory, extracted_name)

            process_xml_file(xml_path, extracted_path)
            extracted_files.append(extracted_path)

    # Step 2: Process extracted_*.txt → structured_*.txt
    structured_files = []
    for file_name in os.listdir(output_directory):
        if file_name.startswith("extracted_") and file_name.endswith(".txt"):
            base_name = file_name.replace("extracted_", "")
            base_name = os.path.splitext(base_name)[0]  # remove .txt
            extracted_path = os.path.join(output_directory, file_name)
            structured_name = f"structured_{base_name}.txt"
            structured_path = os.path.join(output_directory, structured_name)

            process_text_file(extracted_path, structured_path)
            structured_files.append(structured_path)

    # Step 3: Delete the intermediate extracted_*.txt
    for extracted_path in extracted_files:
        try:
            os.remove(extracted_path)
        except Exception as e:
            print(f"❌ Error deleting {extracted_path}: {e}")

    # Step 4: Balance/shuffle each structured_*.txt → label_processed_*.txt
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

    # Step 5: Delete the intermediate structured_*.txt files
    for structured_path in structured_files:
        try:
            os.remove(structured_path)
        except Exception as e:
            print(f"❌ Error deleting {structured_path}: {e}")



input_directory = r"E:\Shadowing\Scope 2\Main_Files\XML FILES\test\xml_file"
output_directory = r"E:\Shadowing\Scope 2\Main_Files\XML FILES\test\xml_file\file_xml"

process_directory(input_directory, output_directory)
print("Full pipeline completed successfully!")
