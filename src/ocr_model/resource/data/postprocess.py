import pandas as pd
from . import util
from ..models import util_model

def remove_course_name(text: str, course_name: str):
  text = text.replace(course_name, "")
  text = text.replace('ง', '4')
  return text

def remove_courseID(text: str, courseID: str):
   text = text.replace(courseID, "")
   return text

def clip_grade_unit(num):
  if num > 4:
     num =  999
  elif num < 4 and num > 3:
     num = 3.5
  elif num < 3 and num > 2:
     num = 2.5
  elif num < 2 and num > 1:
     num = 1.5
  elif num < 1 and num > 0:
     num = 0.5
  return num

def edit_courseID(courseID: str):
  if courseID[0] in ['1', '!', 'เ']:
      courseID =  "I" + courseID[1:]
  if courseID[0] in ['า', '7']:
    courseID =  "ว" + courseID[1:]
  if courseID[0] in ['ล']:
    courseID =  "ส" + courseID[1:]
  if courseID[0] in ['@', '0', 'ธ']:
     courseID = "อ" + courseID[1:]
  if courseID[0] in ['ห']:
     courseID = "ท" + courseID[1:] 
  return courseID

def get_partition(n: int):
    result = 1/n
    return [result] * n 

def slice_image(image, n: int):
    vertical_percentages = get_partition(n)
    # Load the image
    width, height = image.size

    # Calculate vertical slice points
    vertical_points = [0] + [int(height * sum(vertical_percentages[:i+1])) for i in range(len(vertical_percentages))]
    
    # Slice the image and store each window
    slices_dict = {}
    for i in range(len(vertical_points) - 1):
        upper = vertical_points[i]
        lower = vertical_points[i + 1]
        slice_img = image.crop((0, upper, width, lower))
        slices_dict[i] = slice_img
    return slices_dict

def focus_subject(image, subject_index: int, pad: int):
    width, height = image.size
    text_height_percent = 2.6
    
    # Calculate the height of each line in pixels using the given percentage
    line_height = (text_height_percent / 100) * height
    pading = line_height*pad#pading เอาไว้แก้ขอบบน ขอบล่าง

    if(int(subject_index * line_height)-pading < 0):
        top_y = 0 
    else:
        top_y = int(subject_index * line_height)-pading
    if(int((subject_index + 1) * line_height)+pading > height):
        bottom_y = height
    else:
        bottom_y = int((subject_index + 1) * line_height)+pading
    cropped_image = image.crop((0, top_y, width, bottom_y))
    return cropped_image

def recover_error(courses_df: pd.core.frame.DataFrame, image_dict: dict):
  #best bigdog the core engineer. always love you my bois
  error_df = util.get_error(courses_df).reset_index(drop=True)
  for error_record in error_df.values:
    section_idx = error_record[2]
    section_image = image_dict[int(section_idx[0])]

    pads = [12, 10, 8, 6, 4]
    for pad in pads:
        focus_image = focus_subject(section_image, int(section_idx[1:]), pad)
        # focus_image.show()
        focus_text = util_model.images_to_texts({section_idx[0]: focus_image})
        focus_df = util.make_course(focus_text)
        focus_df = util.get_non_error(focus_df)
        is_help = True if (error_record[3] in focus_df['ref'].to_list()) else False
        if is_help:
            correct_record = focus_df.loc[focus_df['ref'] == error_record[3]]
            correct_record = correct_record.reset_index(drop=True)
            correct_record['section'] =  section_idx
            courses_df[(courses_df['ref'] == correct_record['ref'][0]) & (courses_df['section'] == correct_record['section'][0])] = correct_record.loc[0].to_list()
            break
    error_df = util.get_error(courses_df).reset_index(drop=True)
  return courses_df

def pipeline(courses_df: pd.core.frame.DataFrame, image_dict: dict):
   courses_df = recover_error(courses_df, image_dict)
   return courses_df



