from . import preprocess, postprocess
from ..models import util_model
import re
import pandas as pd

def filter_course(text: str):
  text = text.strip()
  pattern = r'[\u0E00-\u0E7F|0-9|๑-๙]{0,1}[0-9|๑-๙]{5}'
  if re.search(pattern, text):
    return text.replace("|", " ")
  return 

def get_line_ref(text: str):
   text = text.strip()
   pattern = r'[\u0E00-\u0E7F]{2}'
   result = re.findall(pattern, text)
   return result[0]


def get_courseID(text: str):
  pattern = r'[\u0E00-\u0E7F|0-9|\!|\@]{1}[0-9]{5}'
  result = re.findall(pattern=pattern, string=text)
  if result:
    result = postprocess.edit_courseID(result[0])
    pattern = r'[ท|ส|ค|ว|อ|พ|ศ|ง|I|ญ|จ|ฝ|ย]'
    if re.findall(pattern=pattern, string=result):
       return result
  print("Error from get_courseID")
  print(text)
  return "999"

def get_course_name(text: str):
  text = postprocess.remove_courseID(text, get_courseID(text))
  pattern = r'(\s[\u0E00-\u0E7F|A-z|\/|0-9]{3,})+' 
  result = re.findall(pattern=pattern, string=text)
  if result:
      return result[0].strip()
  
  print("Error from get_course_name")
  print(text)
  return "999"

def remove_unallowc(allowed_chars: str, text: str):
  pattern = f"[^{re.escape(allowed_chars)}]"
  result = re.sub(pattern=pattern, repl='', string=text)
  return result

def get_numeric(text: str):
  text = postprocess.remove_course_name(text, get_course_name(text))
  text = text.replace("!", " ")
  pattern = r'[\s]{1,}.+'
  result = re.findall(pattern=pattern, string=text)
  if result:
    result = result[0]
  else:
    print("Error from get_numeric")
    print(text)
    return "999"
  result = remove_unallowc("12345 ", result)
  return result.strip()

def get_back_unit(num_list: list):
  unit = num_list[0]
  if unit > 50:
     unit/=100
  return unit

def get_unit(num_list: list):
  unit = num_list[0]
  num = postprocess.clip_grade_unit(unit)
  return num

def get_grade(num_list: list):
  grade = num_list[1]
  num = postprocess.clip_grade_unit(grade)
  if num == 0.5:
     num = 999
  return num

def get_unique_characters(text):
    return ''.join(sorted(set(text)))

def get_grade_and_unit(text: str):
  blocks = text.split()
  unit = 999
  grade = 999
  if len(blocks) > 2:
    blocks = blocks[-2:]

  if len(blocks) == 2:
    for idx, block in enumerate(blocks):
      digit = float(get_unique_characters(block))
      if digit > 4:
        digit /= 10
      blocks[idx] = digit
    unit = blocks[0]
    grade = blocks[1]

  return [unit, grade]

def delete_not_cat(text: str):
  text = text.strip().replace("|", "")
  for cat in ["ภาษาไทย", "คณิตศาสตร์", "วิทยาศาสตร์", "สังคมศึกษา",
              "สุขศึกษา", "ศิลปะ", "การงานอาชีพ", "ภาษาต่างประเทศ",
              "ศึกษาค้นคว้าด้วยตนเอง", "ผลการเรียน"]:
     if cat in text:
        return text
  return

def get_cat(text: str):
  for cat in ["ภาษาไทย", "คณิตศาสตร์", "วิทยาศาสตร์", "สังคมศึกษา",
            "สุขศึกษา", "ศิลปะ", "การงานอาชีพ", "ภาษาต่างประเทศ",
            "ศึกษาค้นคว้าด้วยตนเอง", "ผลการเรียน"]:
    if cat in text:
        return cat
  return "999"

def get_back_weight(text: str):
    pattern = r'[0-9][0-9|\.|\s]+'
    result = re.findall(pattern=pattern, string=text)
    unit, grade = 999, 999
    if result:
      result = result[0].strip()
      result = remove_unallowc(".0123456789 ", result)
      result_list = result.split()
      if (len(result_list) == 2):
         unit, grade = result_list[0], result_list[1]
    else:
      print("Error from get_numeric")
      print(text)
    return [float(unit), float(grade)]

   

def get_GPA(text: str):
   words = pd.Series(text.split('\n'))
   contain_cat = words.apply(delete_not_cat).dropna()
   cats = contain_cat.apply(get_cat)
   weight = contain_cat.apply(get_back_weight)
   unit = weight.apply(get_back_unit)
   grade = weight.apply(get_grade)
   gpa_dict = {"ocr": contain_cat.to_list(),
               "category": cats.to_list(),
               "unit": unit.to_list(),
               "grade": grade.to_list()}
   return pd.DataFrame(gpa_dict)


def get_course(text: str, idx: int):
  words = pd.Series(text.split('\n'))
  courses = words.apply(filter_course).dropna()
  course_ref = courses.apply(get_line_ref)
  course_ids = courses.apply(get_courseID).dropna()
  course_names = courses.apply(get_course_name)
  course_numeric = courses.apply(get_numeric)
  course_weight = course_numeric.apply(get_grade_and_unit)
  course_unit = course_weight.apply(get_unit)
  course_grade = course_weight.apply(get_grade)

  course_dict = {"ocr": courses.to_list(),
                 "numeric": course_numeric.to_list(),
                 "section": [f"{idx}{i:02d}" for i in range(courses.shape[0])],
                 "ref": course_ref.to_list(),
                 "id": course_ids.to_list(),
                 "name": course_names.to_list(),
                 "unit": course_unit.to_list(),
                 "grade": course_grade.to_list(),
                 }
  return course_dict

def verify_courses(course_dict: dict):
    unique_size = 0
    each_size = 0
    for k, v in course_dict.items():
        each_size = len(v)
        unique_size += each_size
    unique_size /= len(course_dict)
    return True if unique_size == each_size else False

def make_course(text_dict: dict):
    courses_df = pd.DataFrame()
    for idx, text in text_dict.items():
        courses = get_course(text, idx)
        if not verify_courses(courses):
            raise ValueError("Amount Record's not balance.")
        courses_df = pd.concat([courses_df, pd.DataFrame(courses)])
    return courses_df.reset_index(drop=True).sort_values(['section'], ascending=True)

def get_error(df: pd.core.frame.DataFrame):
    return df.loc[(df.id == "999") | (df.name == "999") | (df.unit == 999) | (df.grade == 999)]

def get_non_error(df: pd.core.frame.DataFrame):
    return df.loc[~((df.id == "999") | (df.name == "999") | (df.unit == 999) | (df.grade == 999))]


def pre_process(image_dict):
    for k, v in image_dict.items():
        image_dict[k] = preprocess.pipeline(v)
    return image_dict

def post_process(courses_df: pd.core.frame.DataFrame, image_dict: dict):
   return postprocess.pipeline(courses_df, image_dict)