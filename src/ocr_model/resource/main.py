import PyPDF2
from .data import util
from .models import util_model
import os
from pdf2image import convert_from_path

def turn_to_dict(df):
    json_data = {
        "length": len(df),
        "data": df.to_dict(orient='index')
    }
    return json_data

def pdf_to_png(pdf_path, dpi=76):

    images = convert_from_path(pdf_path, dpi)
    print(type(images[0]))

    return images

def doRequestOCR(path: str):
    path_parts = path.split(".")

    if path_parts[-1] == "pdf":
        pdf_path = os.path.join('src', 'ocr_model', 'data', 'raw', path)
        
        imgs = pdf_to_png(pdf_path)

        if len(imgs) >= 2:
            front_image = imgs[0]
            # back_image = imgs[1]

            # print(front_image)
            # print(back_image)

            front_section_dict = util_model.detect_section(front_image, util_model.front_model)
            pf_sections = util.pre_process(front_section_dict)
            front_text_dict = util_model.images_to_texts(pf_sections)
            courses_df = util.make_course(front_text_dict)
            post_courses_df = util.post_process(courses_df, pf_sections)

            # back_section_dict = util_model.detect_section(back_image, util_model.back_model)
            # pb_sections = util.pre_process(back_section_dict)
            # back_text_dict = util_model.images_to_texts(pb_sections)
            # gpa = util.get_GPA(back_text_dict[0])
            
            front_edf = post_courses_df[["id", "name", "unit", "grade"]]
            # back_edf = gpa[["category", "unit", "grade"]]

            front_json = turn_to_dict(front_edf)
            # back_json = turn_to_dict(back_edf)
            back_json = {}
            return front_json, back_json

    return None, None
