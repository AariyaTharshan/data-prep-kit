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

from data_processing.data_access import DataAccessFactory
from kfp_support.workflow_support.utils import KFPUtils, execute_ray_job


if __name__ == "__main__":
    import argparse

    """
    This implementation is not completely generic. It is based on the assumption
    that there is 1 additional data access and it is S3 base. A typical example for such
    use case is usage of 2 S3 buckets with different access credentials -
    one for the data access and one for the additional data, for example, config files, models, etc.
    """
    parser = argparse.ArgumentParser(description="Execute Ray job operation")
    parser.add_argument("--ray_name", type=str, default="")
    parser.add_argument("--run_id", type=str, default="")
    parser.add_argument("--additional_params", type=str, default="{}")
    parser.add_argument("--server_url", type=str, default="")
    parser.add_argument("--prefix", type=str, default="")
    # The component converts the dictionary to json string
    parser.add_argument("--exec_params", type=str, default="{}")
    parser.add_argument("--exec_script_name", default="transformer_launcher.py", type=str)

    args = parser.parse_args()
    cluster_name = KFPUtils.runtime_name(
        ray_name=args.ray_name,
        run_id=args.run_id,
    )
    # convert exec params to dictionary
    exec_params = KFPUtils.load_from_json(args.exec_params)
    # convert s3 config to proper dictionary to use for data access factory
    s3_config = exec_params.get("data_s3_config", "None")
    if s3_config == "None" or s3_config == "":
        s3_config_dict = None
    else:
        s3_config_dict = KFPUtils.load_from_json(s3_config.replace("'", '"'))
    # get and build S3 credentials
    access_key, secret_key, url = KFPUtils.credentials()
    # Create data access factory and data access
    data_factory = DataAccessFactory()
    data_factory.apply_input_params(
        args={
            "data_s3_config": s3_config_dict,
            "data_s3_cred": {"access_key": access_key, "secret_key": secret_key, "url": url},
        }
    )
    data_access = data_factory.create_data_access()
    # extra credentials
    prefix = args.prefix
    extra_access_key, extra_secret_key, extra_url = KFPUtils.credentials(
        access_key=f"{prefix}_S3_KEY", secret_key=f"{prefix}_S3_SECRET", endpoint=f"{prefix}_ENDPOINT"
    )
    # enhance exec params
    exec_params["data_s3_cred"] = (
        "{'access_key': '" + access_key + "', 'secret_key': '" + secret_key + "', 'url': '" + url + "'}"
    )
    exec_params[f"{prefix}_s3_cred"] = (
        "{'access_key': '"
        + extra_access_key
        + "', 'secret_key': '"
        + extra_secret_key
        + "', 'url': '"
        + extra_url
        + "'}"
    )
    # Execute Ray jobs
    execute_ray_job(
        name=cluster_name,
        d_access=data_access,
        additional_params=KFPUtils.load_from_json(args.additional_params),
        e_params=exec_params,
        exec_script_name=args.exec_script_name,
        server_url=args.server_url,
    )
