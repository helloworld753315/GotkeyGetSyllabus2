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

        page = doc[0]
        text_blocks = page.get_text("dict")["blocks"]

        # ---------後で消す--------
        # with open('tmp/com_humanculture2023_1.json', 'w') as json_file:
        #     json.dump(text_blocks, json_file, indent=4, ensure_ascii=False)

        text_field_bounds = self.import_bbox()

        syllabus_list = []
        syllabus_info = {}

        for obj in text_blocks:
            lines = obj['lines']
            for line in lines:
                bbox = list(map(float, line['bbox']))
                text = line['spans'][0]['text']
                for item in text_field_bounds[1:]:
                    param, x, y = item[0], float(item[1]), float(item[2])
                    
                    if bbox[0] == x and bbox[1] == y:
                        syllabus_info.setdefault(param, text)
                        print(text)
                    # else:
                    #     print(f'設定座標 x: {x}, y: {y}')
                    #     print(f'PDFの座標 x: {bbox[0]}, y: {bbox[1]}')
                    #     print(f'テキスト: {text}')
                    print(syllabus_info)

    
    def _load(self):
        print("----------------------------------------------------------------")
        
        doc = fitz.open(self.import_path)

        number_of_pages = doc.page_count
        print(f'pages: {number_of_pages}')

        page = doc[0]
        text_blocks = page.get_text("dict")["blocks"]

        # ---------後で消す--------
        # with open('tmp/com_humanculture2023_1.json', 'w') as json_file:
        #     json.dump(text_blocks, json_file, indent=4, ensure_ascii=False)

        text_field_bounds = self.import_bbox()

        syllabus_list = []
        syllabus_info = {}

        field_bounds_dict = {(float(item[1]), float(item[2])): item[0] for item in text_field_bounds[1:]}

        print(field_bounds_dict)
        print(f'length : {len(list(field_bounds_dict))}')

        for obj in text_blocks:
            lines = obj['lines']
            for line in lines:
                bbox = tuple(map(float, line['bbox'][:2])) # (x, y)のタプルとして格納
                text = line['spans'][0]['text']
                
                # 辞書から直接キーを検索
                if bbox in field_bounds_dict:
                    param = field_bounds_dict[bbox]
                    syllabus_info.setdefault(param, text)
                    # print文はデバッグ時以外はコメントアウトする
        print(syllabus_info)