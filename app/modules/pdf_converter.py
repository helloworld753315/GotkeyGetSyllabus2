import fitz
from pprint import pprint
import json
import csv
import math



class Syllabus:
    # def load():
    #     print("----------------------------------------------------------------")
    #     doc = fitz.open('files/com_humanculture2023.pdf')
    #     page = doc[0]  # first page

    #     text_info = page.get_text("dict", sort=True)
    #     # テキストブロックと座標情報の取得
    #     for block in text_info["blocks"]:
    #         if block["type"] == 0:  # テキストブロックを意味する
    #             bbox = block["bbox"]  # ブロックの座標情報
    #             for line in block["lines"]:
    #                 for span in line["spans"]:
    #                     text = span["text"]  # テキスト内容
    #                     # print(f"Text: {text}, BBox: {bbox}")
    #                     if int(bbox[0]) == 31 and int(bbox[1]) == 44:
    #                         print(f"Text: 科目名 {text}, BBox: {bbox}")

    def import_bbox(path='bbox.csv'):
        with open(path) as f:
            reader = csv.reader(f)
            return list(reader)

    def load():
        file_type = 'pdf'
        path = f'files/com_humanculture2023.{file_type}'
        print("----------------------------------------------------------------")
        pdf_path = 'files/com_humanculture2023.pdf'
        
        doc = fitz.open(pdf_path)

        number_of_pages = doc.page_count
        print(f'pages: {number_of_pages}')

        page = doc[1]
        text_objects = page.get_text("dict")["blocks"]

        text_objects_debug = text_objects[:5]

        text_field_bounds = Syllabus.import_bbox()

        syllabus_list = []
        syllabus_info = {}

        for obj in text_objects:
            bbox = list(map(float, obj['bbox']))
            text = obj['lines'][0]['spans'][0]['text']
        
            for item in text_field_bounds[1:]:
                param, x, y = item[0], float(item[1]), float(item[2])
                
                if bbox[0] == x and bbox[1] == y:
                    syllabus_info.setdefault(param, text)
                    print(text)
        print(syllabus_info)



            

        # for obj in text_objects_debug:
        #     pprint(obj)

        # json_path = 'files/com_humanculture2023.jsonl' 

        # with open(json_path, mode='w', encoding='utf-8') as fout:
        #     for obj in text_objects:
        #         pprint(obj)
        #         json.dump(obj, fout, ensure_ascii=False)
        #         fout.write('\n')