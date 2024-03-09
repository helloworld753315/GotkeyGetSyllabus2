import warnings
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
        return ord(c) - ord('A')

    # def load(self):
    #     # エクセルのマクロが原因だろうと思われる警告の無視
    #     warnings.filterwarnings("ignore", message="Unknown extension is not supported and will be removed")

    #     use_cols = list(map(TimeTable.str_to_int, self.use_cols))
    #     use_colmn_names = [self.column_names[i] for i in use_cols]
    #     df = pd.read_excel(self.import_path, sheet_name=0, skiprows=self.skip_rows, usecols=use_cols)
    #     df.columns = use_colmn_names
    #     return df
    
    def load(self):
        book = excel.load_workbook(self.import_path)
        sheet = book.worksheets[0]
        use_cols = list(map(TimeTable.str_to_int, self.use_cols))
        print(use_cols)
        use_colmn_names = [self.column_names[i] for i in use_cols]
        print(use_colmn_names)

        timetable_list = []
        for row in range(1 + self.skip_rows, sheet.max_row + 1):
            # row_data = [sheet[f'{col}{row}'].value for col in self.use_cols]
            class_details = {}
            for col in self.use_cols:
                value_in_cell = sheet[f'{col}{row}'].value
                use_col = TimeTable.str_to_int(col)
                class_details[f'{self.column_names[use_col]}'] = value_in_cell

            timetable_list.append(class_details)
        return timetable_list

    def export_json(self):
        timetable_list = self.load()
        with open(self.export_path, 'w') as json_file:
            json.dump(timetable_list, json_file, indent=4, ensure_ascii=False)



