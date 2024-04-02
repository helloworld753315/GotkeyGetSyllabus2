import os
import fitz
from pprint import pprint
import json
import csv
import re
import requests, shutil
from pathlib import Path
import urllib.parse
from bs4 import BeautifulSoup

class Syllabus:
    def __init__(self, url, import_path, export_path, text_bbox_setting):
        self.url = url
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

    def export_pdf_to_json(self, num, export_path='tmp/com_humanculture2023_23.json'):
        """デバッグ用の関数。指定したページのPDFをdictで取得して全てjsonファイルに出力する。

        Args:
            num (int): ページ番号
            export_path (str): ファイルを出力するパス
        """
        pages = fitz.open(self.import_path)
        page = pages[num]
        with open(export_path, 'w') as json_file:
            json.dump(page.get_text("dict")["blocks"], json_file, indent=4, ensure_ascii=False)

    def import_pdf(self):
        pages = fitz.open(self.import_path)
        number_of_pages = pages.page_count

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

        return syllabus_list

    def download_to_file(self, url, save_path):
        file_path_obj = Path(save_path)

        if not file_path_obj.parent.exists():
            file_path_obj.parent.mkdir(parents=True)

        if not file_path_obj.exists():
            file_path_obj.touch(exist_ok=True)
            res = requests.get(url, stream=True)
            if res.status_code != 200:
                raise IOError('Could not download:', url)
            with open(save_path, 'wb') as fp:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, fp)
        else:
            print(f'{save_path} exists.')
    
    def get_page(self, url):
        res = requests.get(url)
        if not res.ok:
            return f"Failure. status: {res.status_code}, reason: {res.reason}"
        else:
            html = res.content
            return html
        
    def get_urls_by_group(self):
        """科目群のページからシラバスのURLを取得する。

        Returns:
            list: シラバスのURL一覧
        """
        # URLをデコード
        url = urllib.parse.unquote(self.url)

        split_url = url.split('/')
        save_path = f".cache/{'/'.join(split_url[-3:])}"
        parent_path_from_url = f"{'/'.join(split_url[:-1])}"

        self.download_to_file(url, save_path)

        with open(save_path , encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='normal')
        course_urls = table.find_all('a')
        href_values = [f"{parent_path_from_url}/{url.get('href')}" for url in course_urls]
        print(f'取得したURL数: {len(href_values)}')

        return href_values

    def get_data_by_regex_match(text):
        """／がついた英単語の文字列を取ってくる。

        Args:
            text (str): キーになる文字列

        Returns:
            str: ／がついた英単語の文字列を返す。マッチしなかった場合空白文字を返す。
        """
        pattern = re.compile(r'／([\*A-Za-z\s]*[A-Za-z][\*A-Za-z\s]*)')
        match = pattern.search(text)
        if match:
            # マッチした部分を取得し、改行コードや空白を除去
            result = match.group(1).replace('\n', '').strip()
            return result
        else:
            return ""
    
    def to_camel_case(text):
        words = text.split()
        camel_case_text = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        
        return camel_case_text
    
    def get_key_col_text(self, text):
        """表の列に含まれるテキストから英単語の部分を取得・キャメルケースにしてkeyとして返す。

        Args:
            text (str): 表の列部分のテキスト。

        Returns:
            str: キャメルケースでテキストを返す
        """
        key = Syllabus.get_data_by_regex_match(text)
        key = Syllabus.to_camel_case(key)
        key = key.replace('*', '')

        return key

    def scraping(self):
        syllabus_list = []
        url = 'https://www2.okiu.ac.jp/syllabus/2024/syllabus_%E4%BA%BA%E9%96%93%E6%96%87%E5%8C%96%E7%A7%91%E7%9B%AE%E7%BE%A4/8002/8002_0110320001_ja_JP.html'
        save_path = '.cache/8002_0110320001_ja_JP.html'
        self.download_to_file(url, save_path)

        with open(save_path , encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', class_='syllabus-normal')
        basic_information = tables[0] # 基本情報
        instructor_information = tables[1] # 担当教員情報
        detailed_information = tables[2] # 詳細情報
        class_schedule_details = tables[3] # 授業計画詳細情報

        # 基本情報の取得
        keys = basic_information.findAll('th', class_='syllabus-prin')
        values = basic_information.findAll('td', class_='syllabus-break-word')
        if len(keys) == len(values):
            # basic_information_dict = [{self.get_data_by_regex_match(key.text): Syllabus.replace_fullwidth_space(value.text, "\n")} for key, value in zip(keys, values)]
            basic_information_dict = {self.get_key_col_text(key.text): Syllabus.replace_fullwidth_space(value.text, "\n") for key, value in zip(keys, values)}
        else:
            basic_information_dict = {}

        # 担当教員情報の取得
        keys = instructor_information.findAll('th', class_='syllabus-prin')
        values = instructor_information.findAll('td', class_='syllabus-top-info')
        if len(keys) == len(values):
            # instructor_information_dict = [{self.get_data_by_regex_match(key.text): Syllabus.replace_fullwidth_space(value.text, "\n")} for key, value in zip(keys, values)]
            instructor_information_dict = {self.get_key_col_text(key.text): Syllabus.replace_fullwidth_space(value.text, "\n") for key, value in zip(keys, values)}
        else:
            instructor_information_dict = {}

        # print(f'集計 key: {len(keys)}, values: {len(values)}')

        # 詳細情報の取得
        keys = detailed_information.findAll('th', class_='syllabus-prin')
        index = [0, 1, 3, 4, 5, 7, 8, 9, 10, 11]
        filtered_keys = [keys[i] for i in index]
        values = detailed_information.findAll('td', class_='syllabus-break-word')
        filtered_values = [values[i] for i in index]

        # for k in filtered_keys:
        #     print(f'keys: {k.text}')
        if len(filtered_keys) == len(filtered_values):
            # detailed_information_dict = [{self.get_data_by_regex_match(key.text): Syllabus.replace_fullwidth_space(value.text, "\n")} for key, value in zip(filtered_keys, filtered_values)]
            detailed_information_dict = {self.get_key_col_text(key.text): Syllabus.replace_fullwidth_space(value.text, "\n") for key, value in zip(filtered_keys, filtered_values)}
        else:
            detailed_information_dict = {}

        # print(f'keys: {len(keys)}, filterd_keys: {len(filtered_keys)}, values: {len(values)}, filterd_values: {len(filtered_values)}')

        # 授業計画
        elements_theme = class_schedule_details.select("tr > td:nth-of-type(3)")
        theme = [Syllabus.replace_fullwidth_space(el.text, "\n") for el in elements_theme]
        # 時間外学習の内容
        elements_homework = class_schedule_details.select("tr > td:nth-of-type(4)")
        homework = [Syllabus.replace_fullwidth_space(el.text, "\n") for el in elements_homework]

        syllabus_dict = {**basic_information_dict, **instructor_information_dict, **detailed_information_dict}
        syllabus_dict['theme'] = theme
        syllabus_dict['homework'] = homework


        return syllabus_dict

    def export_json(self):
        """Summary line.
        
        シラバスをjsonファイルとして出力する
        
        """
        syllabus_list = self.scraping()

        with open(self.export_path, 'w') as json_file:
            json.dump(syllabus_list, json_file, indent=4, ensure_ascii=False)