import pandas as pd
import yaml
from modules.timetable import TimeTable
from modules.syllabus import Syllabus
import time


def main():
    with open('config.yml') as file:
        config = yaml.load(file, Loader=yaml.Loader)
    timetable_config = config["timetable"]
    syllabus_config = config["syllabus"]

    print("================================")

    timetable = TimeTable(
        import_path=timetable_config["import_path"],
        export_path=timetable_config["export_path"],
        column_names=timetable_config["column_names"],
        skip_rows=timetable_config["skip_rows"],
        use_cols=timetable_config["use_cols"]
    )
    timetable.export_json()

    start = time.time()
    syllabus = Syllabus(
        import_path=syllabus_config["import_path"],
        export_path=syllabus_config["export_path"],
        text_bbox_setting = syllabus_config["text_bbox_setting"]
    )
    syllabus.load()
    end = time.time()
    time_diff = end - start
    print(f'run_time: {time_diff} s')
    

if __name__ == "__main__":
    main()
