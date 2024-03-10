import openpyxl as excel
import json


class TimeTable:
    def __init__(self, import_path, export_path, column_names, skip_rows, use_cols):
        self.import_path = import_path
        self.export_path = export_path
        self.column_names = column_names
        self.skip_rows = skip_rows
        self.use_cols = use_cols

    def str_to_int(c):
        """Summary line.
        
        エクセルの列名を数値に変換する
        
        Args:
            c (str): エクセルの列
        
        Returns:
            int: 数値に変換した値
        
        """

        return ord(c) - ord('A')
    
    def load(self):
        """Summary line.
        
        エクセルの時間割を読み込む。
        
        Returns:
            list: 時間割のオブジェクトが格納されたリスト
        
        """

        book = excel.load_workbook(self.import_path)
        sheet = book.worksheets[0]

        timetable_list = []
        for row in range(1 + self.skip_rows, sheet.max_row + 1):
            class_details = {}
            for col in self.use_cols:
                value_in_cell = sheet[f'{col}{row}'].value
                use_col = TimeTable.str_to_int(col)
                class_details[f'{self.column_names[use_col]}'] = value_in_cell

            timetable_list.append(class_details)
        return timetable_list

    def export_json(self):
        """Summary line.
        
        時間割をjsonファイルとして出力する
        
        """
        timetable_list = self.load()
        with open(self.export_path, 'w') as json_file:
            json.dump(timetable_list, json_file, indent=4, ensure_ascii=False)



