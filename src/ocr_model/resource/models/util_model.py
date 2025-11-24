from ultralytics import YOLO
import pytesseract
from pathlib import Path
from ..data import preprocess
import re
import os

os.environ["TESSDATA_PREFIX"] = "src/ocr_model/data/model/tesseract/build/tessdata"
front_model = YOLO(Path("src/ocr_model/data/model/yolo/front-model.pt"))
back_model = YOLO(Path("src/ocr_model/data/model/yolo/back-model.pt"))
tesseract_path = Path("src/ocr_model/data/model/tesseract/build/tesseract")

tesseract_config = r"--oem 3 --psm 6"
pytesseract.pytesseract.tesseract_cmd = tesseract_path



def get_ocr_text(image):
  return pytesseract.image_to_string(image=image, lang='thnd', config=tesseract_config)

def get_ocr_data(image):
  return pytesseract.pytesseract.image_to_data(image=image, lang='thnd', config=tesseract_config, output_type="data.frame")

def get_lines_pos(image):
    data = get_ocr_data(image)
    line_pos = []
    allow = True
    texts = data.text.to_list()
    pattern = r'[0-9]'
    for idx, text in enumerate(texts):
        if type(text) == float:
            allow = True
        if allow and (type(text) == str):
            if re.findall(pattern, text):
              line_pos.append(data.iloc[idx, [6, 7, 8, 9, 11]].to_dict())
              allow = False
    return line_pos

def images_to_texts(image_dict: dict):
  ocr_dict = {}
  for k, v in image_dict.items():
    text = get_ocr_text(v)
    ocr_dict[k] = text
  return ocr_dict
  

def detect_section(image, yolo_model):
  cv2_image = preprocess.pil_to_cv2(image)
  coords = yolo_model(image, conf=0.8)

  section_dict = {}
  boxes = [box for data in coords for box in data.boxes.data]
  for idx, box in enumerate(boxes):
    x, y, h, w, _, _ = box
    x, y, h, w = int(x), int(y), int(w), int(h)
    croped_img = cv2_image[y:h, x:w]
    section_dict[idx] = preprocess.cv2_to_pil(croped_img)
  return section_dict





