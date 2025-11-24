from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from ..models import util_model
import pandas as pd
from pathlib import Path
from . import load_data

thai_alphabets = load_data.get_thai_alphabet()

def cv2_to_pil(image):
    return Image.fromarray(image)

def pil_to_cv2(image):
    numpy_image = np.array(image)
    cv2_image = cv2.cvtColor(numpy_image, cv2.IMREAD_GRAYSCALE)
    return cv2_image

def denoise(image):
    cv2_image = pil_to_cv2(image)
    iso_image = cv2.fastNlMeansDenoising(cv2_image, None, h=10, 
                                         templateWindowSize=3, searchWindowSize=21)
    return cv2_to_pil(iso_image)

def add_white_space(image, width_percent: float):
    # Calculate the new width for the white space
    white_space_width = int(image.width * width_percent)

    # Create a new image with white background
    new_width = image.width + white_space_width
    new_img = Image.new("RGB", (new_width, image.height), "white")

    # Paste the original image on the new image, offset by the white space width
    new_img.paste(image, (white_space_width, 0))
    return new_img

def add_line_reference(image, alphabets:list, font_dir:str, font_name:str):
    bb = util_model.get_lines_pos(image)

    # Copy the original image
    drawed_image = image.copy()

    # Create Draw Object
    draw = ImageDraw.Draw(drawed_image)

    # Calculate the width for the whitespace (assuming it is 1% of the image width)
    white_space_width = int(image.width * 0.02)

    df = pd.DataFrame(bb)
    height_med = df.height.median()
    
    # Load a font
    font_path = Path(font_dir)/font_name
    font_size = height_med * (1.7)
    font = ImageFont.truetype(font_path, font_size)

    

    # Extract the bounding box coordinates
    for i in range(len(bb)):
        _, top, _, height, _ = bb[i].values()
        
        # Calculate position for the alphabet
        text_x = white_space_width // 2
        text_y = top - (height_med - (abs(height_med-height)*0.7))/2


        # Draw the alphabet on the image
        draw.text((text_x, text_y), alphabets[i], font=font, fill="black")

    return drawed_image
    

def pipeline(image):
    processed = denoise(image=image)
    processed = add_white_space(processed, 0.1)
    processed = add_line_reference(processed, thai_alphabets, 'src/ocr_model/data/font', 'THSarabunNew.ttf')
    return processed




