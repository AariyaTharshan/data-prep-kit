import os
import sys
from pathlib import Path

from data_processing.ray import TransformLauncher
from data_processing.utils import ParamsUtils
from langselect_transform import (
    LangSelectorTransformConfiguration,
    lang_allowed_langs_file_key,
    lang_known_selector,
    lang_lang_column_key,
)


# create launcher
launcher = TransformLauncher(transform_runtime_config=LangSelectorTransformConfiguration())
# create parameters
language_column_name = "language"

selected_languages_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../test-data/languages/allowed-code-languages.txt")
)

s3_cred = {
    "access_key": DPFConfig.S3_ACCESS_KEY,
    "secret_key": DPFConfig.S3_SECRET_KEY,
    "url": "https://s3.us-east.cloud-object-storage.appdomain.cloud",
}
# Configure lakehouse unit test tables
lakehouse_config = {
    "lh_environment": "STAGING",
    "input_table": "academic.ieee_lh_unittest",
    "input_dataset": "",
    "input_version": "main",
    "output_table": "academic.ieee_langselect_0304_02",
    "output_path": "lh-test/tables/academic/ieee_langselect_0304_02",
    "token": DPFConfig.LAKEHOUSE_TOKEN,
}

worker_options = {"num_cpus": 0.8}
code_location = {"github": "github", "commit_hash": "12345", "path": "path"}
params = {
    "run_locally": True,
    "max_files": -1,
    "s3_cred": ParamsUtils.convert_to_ast(s3_cred),
    "lh_config": ParamsUtils.convert_to_ast(lakehouse_config),
    "worker_options": ParamsUtils.convert_to_ast(worker_options),
    "num_workers": 1,
    "checkpointing": False,
    "pipeline_id": "pipeline_id",
    "job_id": "job_id",
    "creation_delay": 0,
    "code_location": ParamsUtils.convert_to_ast(code_location),
    lang_allowed_langs_file_key: selected_languages_file,
    lang_lang_column_key: language_column_name,
    lang_known_selector: True,
    "lang_select_local_config": ParamsUtils.convert_to_ast(local_conf),
}

if __name__ == "__main__":
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    sys.argv = ParamsUtils.dict_to_req(d=params)
    # launch
    launcher.launch()
