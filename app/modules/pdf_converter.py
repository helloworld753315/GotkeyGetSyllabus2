import fitz
from pprint import pprint
import json


class Syllabus:
    # def load():
    #     with open('files/com_humanculture2023.pdf', 'rb') as file:
    #         reader = pypdf.PdfReader(file)

    #         pdf_pages = reader.pages

    #         number_of_pages = len(pdf_pages)
    #         print(f"Pages: {number_of_pages}")
    #         for page_number, page in enumerate(reader.pages):
    #             print(f"--- Page {page_number + 1} ---")
    #             text_objects = page.extract_text("rawdict")['blocks']
    #             for obj in text_objects:
    #                 if obj['type'] == 0:  # Text object
    #                     x = obj['bbox'][0]
    #                     y = obj['bbox'][1]
    #                     text = obj['text']
    #                     print(f"Text: {text} (x: {x}, y: {y})")
    def load():
        print("----------------------------------------------------------------")
        doc = fitz.open('files/com_humanculture2023.pdf')
        page = doc[0]  # first page

        text_info = page.get_text("dict", sort=True)
        # テキストブロックと座標情報の取得
        for block in text_info["blocks"]:
            if block["type"] == 0:  # テキストブロックを意味する
                bbox = block["bbox"]  # ブロックの座標情報
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]  # テキスト内容
                        # print(f"Text: {text}, BBox: {bbox}")
                        if int(bbox[0]) == 31 and int(bbox[1]) == 44:
                            print(f"Text: 科目名 {text}, BBox: {bbox}")

        # dir = "files/output.json"
        # with open(dir, mode="w", encoding="utf-8") as f:
        #     json.dump(words, f, ensure_ascii=False, indent=2)
        # pprint(words)