
from PIL import Image
import csv
import json
import pandas as pd
import pathlib
from pathlib import Path

def read_image(image_path:str, filename:str):
    for e in [".jpg", ".jpeg", ".png"]:
        try :
            return Image.open(Path(image_path + "/" + filename + e)).convert("L")
        except:
            continue
    raise Exception("Unformat Image")

def export_df_to_csv(csv_path: str, filename: str, df: pd.core.frame.DataFrame):
    csv_file_path = Path(csv_path + "/" + filename + ".csv")
    df.to_csv(csv_file_path, index=False)

def csv_to_json(json_path:str , csv_path:str, filename:str):
    csv_file_path = Path(csv_path + "/" + filename + ".csv")
    json_file_path = Path(json_path + "/" + filename + ".json")

    json_data = {
    "length": 0,
    "data": {}
    }

    # Read the CSV file and populate the JSON structure
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        json_data["length"] = len(rows)
        
        for i, row in enumerate(rows, start=1):
            json_data["data"][str(i)] = row

    # Save the JSON data to a file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

def get_thai_alphabet():
    thai_alphabet = [chr(i) for i in range(ord('ก'), ord('ฮ') + 1)]
    ls = []
    for i in thai_alphabet:
        str = i
        for j in thai_alphabet:
            str += j
            ls.append(str)
            str = i
    return ls