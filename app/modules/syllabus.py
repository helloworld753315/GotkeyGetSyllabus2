import fitz
from pprint import pprint
import json
import csv
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
    

    def check_multipage(self, page, x1=282.7799987792969, y1=815.6806030273438, x2=304.7400207519531, y2=824.6806030273438):
        """複数ページにまたがっているかどうかを検出する。

        Args:
            page (any): PyMuPDFのページオブジェクト
            x1 (float): x1
            y1 (float): y1
            x2 (float): x2
            y2 (float): y2

        Returns:
            int: 単一ページの場合は0, 複数ページの場合は1か2を返す。
        """
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


    def load(self):
        pages = fitz.open(self.import_path)
        number_of_pages = pages.page_count
        # page = pages[22]
        # with open('tmp/com_humanculture2023_23.json', 'w') as json_file:
        #     json.dump(page.get_text("dict")["blocks"], json_file, indent=4, ensure_ascii=False)
        text_field_bounds = self.import_bbox()

        syllabus_list = []
        syllabus_info = {}
        multi_page_count = 0
        for page in pages:
            multi_page_flag = self.check_multipage(page)
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

        print(f'ページ数: {number_of_pages}')
        print(f'複数ページにまたがっているシラバス: {multi_page_count}')
        print(f'シラバスの数: {number_of_pages - (int(multi_page_count / 2))}')
        print(f'取得成功したシラバスの数: {len(syllabus_list)}')

        with open(self.export_path, 'w') as json_file:
            json.dump(syllabus_list, json_file, indent=4, ensure_ascii=False)