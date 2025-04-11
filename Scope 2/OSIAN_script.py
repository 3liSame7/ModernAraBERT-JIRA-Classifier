import os
from farasa.segmenter import FarasaSegmenter
import json
import csv
import re
from itertools import islice
import requests
import zipfile
from io import BytesIO


farasa_segmenter = FarasaSegmenter(interactive=False)


def download_and_extract_txt(country, url, output_dir):
    try:
        print(f"Processing: {country}")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        # Extract ZIP file
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            txt_files = [
                file
                for file in zip_ref.namelist()
                if file.startswith("files/data/sentences") and file.endswith(".txt")
            ]
            if not txt_files:
                print(f"No .txt files found in the ZIP for {country}.")
                return

            country_dir = os.path.join(output_dir, country)
            os.makedirs(country_dir, exist_ok=True)

            for txt_file in txt_files:
                zip_ref.extract(txt_file, country_dir)
                print(f"Extracted {txt_file} to {country_dir}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download dataset for {country}: {e}")
    except zipfile.BadZipFile:
        print(f"Invalid ZIP file for {country}: {url}")


def preprocess_with_farasa(text):
    text = text[1]
    unwanted_chars = r"[()\[\]:«»“”‘’—_,;!?|/\\]"
    text = re.sub(unwanted_chars, "", text)
    text = re.sub(r"(\-\-|\[\]|\.\.)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^\d+\s+", "", text)
    return farasa_segmenter.segment(text)


def read_csv_in_batches(file_path, batch_size=1000):
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        headers = next(reader)  # Read the header separately
        while True:
            batch = list(islice(reader, batch_size))
            if not batch:
                print(batch, "\t", "breaking")
                break
            yield batch  # Return the batch as a generator


# Main script
def main():
    json_file = "OSIAN_Links.json"  # Replace with your JSON file name
    output_dir = "D:\\Work\\ModernBERT\\Data"  # Directory to store extracted files

    # Load the JSON file
    try:
        with open(json_file, "r") as file:
            country_datasets = json.load(file)
    except FileNotFoundError:
        print(f"JSON file {json_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON file {json_file}.")
        return

    # Process each country and its dataset link
    for country, url in country_datasets.items():
        download_and_extract_txt(country, url, output_dir)
        print(f"processing {country} data")
        output_file = os.path.join(
            output_dir, country, "files/data/sentences_segmented.txt"
        )
        txt_file_path = os.path.join(output_dir, country, "files/data/sentences.txt")
        with open(output_file, "a", encoding="utf-8", newline="\n") as f:
            for batch_number, batch in enumerate(
                read_csv_in_batches(txt_file_path, 1000), start=1
            ):
                print(f"Batch {batch_number}: {len(batch)} rows")
                t = list(map(preprocess_with_farasa, batch))
                f.writelines([f"{s}\n" for s in t])


if __name__ == "__main__":
    main()
