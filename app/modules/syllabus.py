import os
import fitz
from pprint import pprint
import json
import csv
import re
import time, random
from tqdm import tqdm
import requests, shutil
from pathlib import Path
import urllib.parse
from bs4 import BeautifulSoup

class Syllabus:
    def __init__(self, url, urls, import_path, export_path, text_bbox_setting):
        self.url = url
        self.urls = urls
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

    def extract_from_pdf(self):
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

    def download_to_html(self, url, save_path):
        file_path_obj = Path(save_path)

        if not file_path_obj.parent.exists():
            file_path_obj.parent.mkdir(parents=True)

        if not file_path_obj.exists():
            file_path_obj.touch(exist_ok=True)
            res = requests.get(url, stream=True)
            time.sleep(random.uniform(1,3))
            if res.status_code != 200:
                raise IOError('Could not download:', url)
            with open(save_path, 'wb') as fp:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, fp)
        else:
            pass
            # tqdm.write(f'{save_path} exists.')

        return save_path
        
    def get_urls_by_group(self, url):
        """科目群のページからシラバスのURLを取得する。

        Returns:
            list: シラバスのURL一覧
        """
        # URLをデコード
        url = urllib.parse.unquote(url)

        split_url = url.split('/')
        save_path = f".cache/{'/'.join(split_url[-3:])}"
        parent_path_from_url = f"{'/'.join(split_url[:-1])}"

        self.download_to_html(url, save_path)

        with open(save_path , encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='normal')
        course_urls = table.find_all('a')
        urls = [f"{parent_path_from_url}/{url.get('href')}" for url in course_urls]
        tqdm.write(f'取得したURL数: {len(urls)}')

        return urls
    
    def get_japanese_only(text):
        # 日本語テキスト（平仮名、片仮名、漢字）にマッチする正規表現パターン
        pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+'
        # 正規表現を使って日本語の部分を抜き出す
        japanese_text = ''.join(re.findall(pattern, text))

        return japanese_text

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
        """半角スペースが含まれたテキストをキャメルケースに変換して返す。

        Args:
            text (str): キャメルケースに変換したいテキスト

        Returns:
            str: キャメルケースに変換したテキストを返す
        """
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
    
    def create_dict_from_pairs(self, keys, values):
        """受け取ったkeyとvalueをペアにして辞書型で返す。

        Args:
            keys (list): キーのリスト。
            values (list): バリューのリスト。

        Returns:
            dict: キーとバリューをペアにして辞書で返す。要素数が一致しなかった場合、空のリストを返す。
        """
        if len(keys) == len(values):
            key_value_pairs = {self.get_key_col_text(key.text): Syllabus.replace_fullwidth_space(value.text, "\n") for key, value in zip(keys, values)}
        else:
            key_value_pairs = {}

        return key_value_pairs

    def extract_from_web(self, url):
        # URLをデコード
        url = urllib.parse.unquote(url)
        split_url = url.split('/')
        save_path = f".cache/{'/'.join(split_url[-4:])}"

        self.download_to_html(url, save_path)

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
        basic_information_dict = self.create_dict_from_pairs(keys, values)

        # 担当教員情報の取得
        keys = instructor_information.findAll('th', class_='syllabus-prin')
        values = instructor_information.findAll('td', class_='syllabus-top-info')
        instructor_information_dict = self.create_dict_from_pairs(keys, values)

        # 詳細情報の取得
        keys = detailed_information.findAll('th', class_='syllabus-prin')
        index = [0, 1, 3, 4, 5, 7, 8, 9, 10, 11]
        filtered_keys = [keys[i] for i in index]
        values = detailed_information.findAll('td', class_='syllabus-break-word')
        filtered_values = [values[i] for i in index]
        detailed_information_dict = self.create_dict_from_pairs(filtered_keys, filtered_values)

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

    def get_syllabus_by_group(self):
        for url in tqdm(self.urls):
            syllabus_urls = self.get_urls_by_group(url)
            for syllabus_url in tqdm(syllabus_urls, total=len(syllabus_urls)):
                self.extract_from_web(syllabus_url)


    def export_json(self):
        """Summary line.
        
        シラバスをjsonファイルとして出力する
        
        """
        url = 'https://www2.okiu.ac.jp/syllabus/2024/syllabus_%E4%BA%BA%E9%96%93%E6%96%87%E5%8C%96%E7%A7%91%E7%9B%AE%E7%BE%A4/8002/8002_0110320001_ja_JP.html'
        save_path = '.cache/8002_0110320001_ja_JP.html'
        syllabus_list = self.extract_from_web(url)

        with open(self.export_path, 'w') as json_file:
            json.dump(syllabus_list, json_file, indent=4, ensure_ascii=False)