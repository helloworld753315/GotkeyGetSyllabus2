import pandas as pd
import warnings


class TimeTable:
    def __init__(self, import_path, column_names, skip_rows, use_cols):
        self.import_path = import_path
        self.column_names = column_names
        self.skip_rows = skip_rows
        self.use_cols = use_cols

    pd.set_option('display.width', 1000)
    pd.set_option('display.max_rows', 20)

    def str_to_int(c):
        return ord(c) - ord('A')

    def load(self):
        # エクセルのマクロが原因だろうと思われる警告の無視
        warnings.filterwarnings("ignore", message="Unknown extension is not supported and will be removed")

        use_cols = list(map(TimeTable.str_to_int, self.use_cols))
        use_colmn_names = [self.column_names[i] for i in use_cols]
        df = pd.read_excel(self.import_path, sheet_name=0, skiprows=self.skip_rows, usecols=use_cols)
        df.columns = use_colmn_names
        print(df)

