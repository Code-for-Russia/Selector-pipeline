from airflow.decorators import dag, task
import jsonlines

from org.codeforrussia.selector.pipeline.input.dump_formats import SupportedInputFormat

default_args = {
    'owner': 'airflow',
    'input_data_path': "/Users/nzhiltsov/Documents/projects/selector/selector-schemas/tests/resources/state_duma_shpilkin_dump.21-09-2020.jsonl",
    'input_data_format': SupportedInputFormat.SHPILKIN_DUMP
}

@dag(default_args=default_args, schedule_interval=None, tags=['selector'])
def selector_standardization():

    @task()
    def import_dumps():
        if default_args["input_data_format"] == SupportedInputFormat.SHPILKIN_DUMP:
            dump_file = default_args["input_data_path"]
            with jsonlines.open(dump_file) as reader:
                for line in reader:
                    
            
        else:
            raise ValueError("Input data format is not supported")





