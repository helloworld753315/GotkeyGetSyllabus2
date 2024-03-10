import fitz
from pprint import pprint
import json
import csv
import math

class Syllabus:
    def __init__(self, import_path, export_path, text_bbox_setting):
        self.import_path = import_path
        self.export_path = export_path
        self.text_bbox_setting = text_bbox_setting

    def replace_fullwidth_space(text, replacement):
        """全角スペースを任意の文字に置き換える。

        Args:
            text (str): 置き換えを行う文字列。
            replacement (str): 全角スペースを置き換えるための文字列。

        Returns:
            str: 全角スペースが置き換えられた文字列。
        """
        formatted_text = text.replace("\u3000", replacement)
    
        return formatted_text

    def import_bbox(self):
        with open(self.text_bbox_setting) as f:
            reader = csv.reader(f)
            return list(reader)

    def load(self):
        print("----------------------------------------------------------------")
        
        doc = fitz.open(self.import_path)

        number_of_pages = doc.page_count
        print(f'pages: {number_of_pages}')

        page = doc[1]
        text_blocks = page.get_text("dict")["blocks"]

        # text_objects_debug = text_objects[:5]

        text_field_bounds = self.import_bbox()

        syllabus_list = []
        syllabus_info = {}

        for obj in text_blocks:
            bbox = list(map(float, obj['bbox']))
            text = obj['lines'][0]['spans'][0]['text']
        
            for item in text_field_bounds[1:]:
                param, x, y = item[0], float(item[1]), float(item[2])
                
                if bbox[0] == x and bbox[1] == y:
                    syllabus_info.setdefault(param, text)
                    print(text)
        print(syllabus_info)