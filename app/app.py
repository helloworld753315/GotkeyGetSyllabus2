import pandas as pd
import yaml
from modules.excel_converter import TimeTable


def main():
    with open('config.yml') as file:
        config = yaml.load(file, Loader=yaml.Loader)
    timetable_config = config["timetable"]
    print("================================")

    timetable = TimeTable(
        import_path=timetable_config["import_path"],
        column_names=timetable_config["column_names"],
        skip_rows=timetable_config["skip_rows"],
        use_cols=timetable_config["use_cols"]
    )
    timetable.load()


if __name__ == "__main__":
    main()
