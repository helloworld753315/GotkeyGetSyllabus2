import fitz
from pprint import pprint
import json
import csv
import math
import re

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
            reader = reader = csv.DictReader(f, skipinitialspace=True)
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

    def check_multipage(self, page, x1=282.7799987792969, y1=815.6806030273438, x2=304.7400207519531, y2=824.6806030273438):
        rect = fitz.Rect(x1, y1, x2, y2)
        target_text = page.get_textbox(rect).replace('\n', '')

        # 正規表現パターン: 全角スラッシュと「1」「2」の数字
        pattern = r"[１1２2]?／[１1２2]?"

        matches = re.findall(pattern, target_text)

        if len(str(target_text)) == 3 and matches:
            if "1" in target_text:
                return 1
            elif "2" in target_text:
                return 2
        else:
            return 0


    def test_load(self):
        pages = fitz.open(self.import_path)
        number_of_pages = pages.page_count
        # page = pages[22]
        # with open('tmp/com_humanculture2023_23.json', 'w') as json_file:
        #     json.dump(page.get_text("dict")["blocks"], json_file, indent=4, ensure_ascii=False)

        # テキストを抽出したい矩形領域を定義 (x0, y0, x1, y1)
        count = 0
        text_field_bounds = self.import_bbox()

        syllabus_list = []
        syllabus_info_multi_page = {}
        syllabus_info = {}
        multi_page_count = 0
        for page in pages:
            multi_page_flag = self.check_multipage(page)
            # syllabus_info = {}
            if not(multi_page_flag == 0):
                multi_page_count += 1
            for row in text_field_bounds:
                # 複数ページにまたがっているかそうでないかで参照する座標を変更
                if multi_page_flag == 0:
                    rect = fitz.Rect(row['s-x1'], row['s-y1'], row['s-x2'], row['s-y2'])
                    text = page.get_textbox(rect)
                    syllabus_info.setdefault(row['params'], text)
                else:
                    rect = fitz.Rect(row['m-x1'], row['m-y1'], row['m-x2'], row['m-y2'])
                    text = page.get_textbox(rect)
                    # csvとflagでページ数が一致するときのみ辞書に追加
                    if multi_page_flag == int(row['m-page-num']):
                        syllabus_info.setdefault(row['params'], text)
                if len(syllabus_info) == len(text_field_bounds):
                    syllabus_list.append(syllabus_info)
                    syllabus_info = {}

            # if self.check_multipage(page):
            #     pass
            # else:
            #     for row in text_field_bounds:
            #         rect = fitz.Rect(row['s-x1'], row['s-y1'], row['s-x2'], row['s-y2'])
            #         # 指定された矩形領域内のテキストを抽出
            #         text = page.get_textbox(rect)
            #         syllabus_info.setdefault(row['params'], text)

            #         # if self.check_multipage(page):
            #         #     lec_count = len(text.split('\n'))
            #         #     if lec_count == 31: # 16
            #         #         count += 1
            #     syllabus_list.append(syllabus_info)
        print(f'ページ数: {number_of_pages}')
        print(f'複数ページにまたがっているシラバス: {multi_page_count}')
        print(f'シラバスの数: {number_of_pages - (int(multi_page_count / 2))}')
        print(f'取得成功したシラバスの数: {len(syllabus_list)}')

        with open('tmp/out/com_humanculture2023_test_0324_2.json', 'w') as json_file:
            json.dump(syllabus_list, json_file, indent=4, ensure_ascii=False)
        
        # print(f'授業回数の一致: {count}')
        # print(f'複数ページのパターン数: {multipage_count}')


    def _load(self):
        print("----------------------------------------------------------------")
        
        doc = fitz.open(self.import_path)

        number_of_pages = doc.page_count
        print(f'pages: {number_of_pages}')

        # ---------後で消す--------
        # with open('tmp/com_humanculture2023_1.json', 'w') as json_file:
        #     json.dump(text_blocks, json_file, indent=4, ensure_ascii=False)

        text_field_bounds = self.import_bbox()

        print(text_field_bounds)

        syllabus_list = []

        field_bounds_dict = {(float(item[1]), float(item[2])): item[0] for item in text_field_bounds[1:]}

        for count, page in enumerate(doc):
            syllabus_info = {}
            # page = doc[0]

            text_blocks = page.get_text("dict")["blocks"]

            with open('tmp/com_humanculture2023_1.json', 'w') as json_file:
                json.dump(doc[0].get_text("dict")["blocks"], json_file, indent=4, ensure_ascii=False)

            for obj in text_blocks:
                lines = obj['lines']
                for line in lines:
                    bbox = tuple(map(float, line['bbox'][:2])) # (x, y)のタプルとして格納
                    text = line['spans'][0]['text']
                    
                    # 辞書から直接キーを検索
                    if bbox in field_bounds_dict:
                        param = field_bounds_dict[bbox]
                        syllabus_info.setdefault(param, text)
            if len(syllabus_info) == len(list(field_bounds_dict)):
                syllabus_list.append(syllabus_info)
            else:
                print(f'failure page: {count}')

        print(f'{len(syllabus_list)}')
        
        with open('tmp/com_humanculture2023_test1.json', 'w') as json_file:
            json.dump(syllabus_list, json_file, indent=4, ensure_ascii=False)