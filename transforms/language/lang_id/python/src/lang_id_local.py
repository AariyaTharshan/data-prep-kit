# (C) Copyright IBM Corp. 2024.
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import os

from data_processing.data_access import DataAccessLocal
from lang_id_transform import (
    LangIdentificationTransform,
    content_column_name_key,
    model_credential_key,
    model_kind_key,
    model_url_key,
)
from lang_models import KIND_FASTTEXT


# create parameters
input_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test-data", "input"))

lang_id_params = {
    model_credential_key: "PUT YOUR OWN HUGGINGFACE CREDENTIAL",
    model_kind_key: KIND_FASTTEXT,
    model_url_key: "facebook/fasttext-language-identification",
    content_column_name_key: "text",
}
if __name__ == "__main__":
    # Here we show how to run outside of the runtime
    # Create and configure the transform.
    transform = LangIdentificationTransform(lang_id_params)
    # Use the local data access to read a parquet table.
    data_access = DataAccessLocal()
    table, _ = data_access.get_table(os.path.join(input_folder, "test_01.parquet"))
    print(f"input table: {table}")
    # Transform the table
    try:
        table_list, metadata = transform.transform(table)
        print(f"\noutput table: {table_list}")
        print(f"output metadata : {metadata}")
    except Exception as e:
        print(f"Exception executing transofm {e}")
