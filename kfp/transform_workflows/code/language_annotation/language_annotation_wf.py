import kfp.compiler as compiler
import kfp.components as comp
import kfp.dsl as dsl
from kfp_support.workflow_support.utils import (
    ONE_HOUR_SEC,
    ONE_WEEK_SEC,
    ComponentUtils,
)
from kubernetes import client as k8s_client


# the name of the job script
EXEC_SCRIPT_NAME: str = "transform/lang_annotator_transform.py"

task_image = "us.icr.io/cil15-shared-registry/preprocessing-pipelines/kfp-data-processing/lang_annotator:0.0.2"

# components
base_kfp_image = "us.icr.io/cil15-shared-registry/preprocessing-pipelines/kfp-data-processing:0.0.4"
# compute execution parameters. Here different tranforms might need different implementations. As
# a result, insted of creating a component we are creating it in place here.
compute_exec_params_op = comp.func_to_container_op(
    func=ComponentUtils.default_compute_execution_params, base_image=base_kfp_image
)
# create Ray cluster
create_ray_op = comp.load_component_from_file("../../../kfp_ray_components/createRayComponent.yaml")
# execute job
execute_ray_jobs_op = comp.load_component_from_file("../../../kfp_ray_components/executeRayJobComponent_multi_s3.yaml")
# clean up Ray
cleanup_ray_op = comp.load_component_from_file("../../../kfp_ray_components/cleanupRayComponent.yaml")
# Task name is part of the pipeline name, the ray cluster name and the job name in DMF.
TASK_NAME: str = "lang_select"
PREFIX: str = "lang_select"

@dsl.pipeline(
    name=TASK_NAME + "-ray-pipeline",
    description="Pipeline for select language",
)
def lang_select(
    ray_name: str = "select-lang-kfp-ray",  # name of Ray cluster
    ray_head_options: str = '{"cpu": 1, "memory": 4, "image_pull_secret": "prod-all-icr-io",\
             "image": "' + task_image + '" }',
    ray_worker_options: str = '{"replicas": 2, "max_replicas": 2, "min_replicas": 2, "cpu": 2, "memory": 4, "image_pull_secret": "prod-all-icr-io",\
            "image": "' + task_image + '" }',
    server_url: str = "http://kuberay-apiserver-service.kuberay.svc.cluster.local:8888",
    additional_params: str = '{"wait_interval": 2, "wait_cluster_ready_tmout": 400, "wait_cluster_up_tmout": 300, "wait_job_ready_tmout": 400, "wait_print_tmout": 30, "http_retries": 5}',
    lh_config: str = "None",
    max_files: int = -1,
    actor_options: str = "{'num_cpus': 0.8}",
    pipeline_id: str = "pipeline_id",
    s3_access_secret: str = "cos-access",
    s3_config: str = "{'input_folder': 'cos-optimal-llm-pile/sanity-test/input-select-lang/input/', 'output_folder': 'cos-optimal-llm-pile/doc_annotation_test/output_select_lang_guf/'}",
    lang_select_allowed_langs_file: str = "cos-optimal-llm-pile/sanity-test/input-select-lang/languages/allowed-code-languages.txt",
    lang_select_language_column: str = "language",
    lang_select_return_known: bool = True,
    lang_select_lh_config: str = "None",
    lang_select_local_config: str = "None",
    lang_select_s3_config: str = "{'input_folder': 'cos-optimal-llm-pile/sanity-test/input-select-lang/input/', 'output_folder': 'cos-optimal-llm-pile/doc_annotation_test/output_select_lang_guf/'}",
    lang_select_s3_access_secret: str = "cos-access",
) -> None:
    """
    Pipeline to execute NOOP transform
    :param ray_name: name of the Ray cluster
    :param ray_head_options: head node options, containing the following:
        cpu - number of cpus
        memory - memory
        image - image to use
        image_pull_secret - image pull secret
    :param ray_worker_options: worker node options (we here are using only 1 worker pool), containing the following:
        replicas - number of replicas to create
        max_replicas - max number of replicas
        min_replicas - min number of replicas
        cpu - number of cpus
        memory - memory
        image - image to use
        image_pull_secret - image pull secret
    :param server_url - server url
    :param additional_params: additional (support) parameters, containing the following:
        wait_interval - wait interval for API server, sec
        wait_cluster_ready_tmout - time to wait for cluster ready, sec
        wait_cluster_up_tmout - time to wait for cluster up, sec
        wait_job_ready_tmout - time to wait for job ready, sec
        wait_print_tmout - time between prints, sec
        http_retries - httpt retries for API server calls
    :param lh_config - lake house configuration
    :param s3_config - s3 configuration
    :param s3_access_secret - s3 access secret
    :param max_files - max files to process
    :param actor_options - actor options
    :param pipeline_id - pipeline id
    :param lang_select_allowed_langs_file - file to store allowed languages
    :param lang_select_language_column - name of select language annotation column
    :param lang_select_return_known - Flag to return docs with known languages (True) or unknown (False).
    :param lang_select_lh_config - lang select lakehouse config
    :param lang_select_local_config - lang select local config
    :param lang_select_s3_config - lang select s3 config
    :param lang_select_s3_access_secret - 
                    (here we are assuming that select language info is in S3, but potentially in the different bucket)
    :return: None
    """
    # create clean_up task
    clean_up_task = cleanup_ray_op(ray_name=ray_name, run_id=dsl.RUN_ID_PLACEHOLDER, server_url=server_url)
    ComponentUtils.add_settings_to_component(clean_up_task, 60)
    # pipeline definition
    with dsl.ExitHandler(clean_up_task):
        # compute execution params
        compute_exec_params = compute_exec_params_op(
            worker_options=ray_worker_options,
            actor_options=actor_options,
        )
        ComponentUtils.add_settings_to_component(compute_exec_params, ONE_HOUR_SEC * 2)
        # start Ray cluster
        ray_cluster = create_ray_op(
            ray_name=ray_name,
            run_id=dsl.RUN_ID_PLACEHOLDER,
            ray_head_options=ray_head_options,
            ray_worker_options=ray_worker_options,
            server_url=server_url,
            additional_params=additional_params,
        )
        ComponentUtils.add_settings_to_component(ray_cluster, ONE_HOUR_SEC * 2)
        ray_cluster.after(compute_exec_params)
        # Execute job
        execute_job = execute_ray_jobs_op(
            ray_name=ray_name,
            run_id=dsl.RUN_ID_PLACEHOLDER,
            additional_params=additional_params,
            # note that the parameters below are specific for NOOP transform
            exec_params={
                "s3_config": s3_config,
                "lh_config": lh_config,
                "max_files": max_files,
                "num_workers": compute_exec_params.output,
                "worker_options": actor_options,
                "pipeline_id": pipeline_id,
                "job_id": dsl.RUN_ID_PLACEHOLDER,
                "lang_select_allowed_langs_file": lang_select_allowed_langs_file,
                "lang_select_language_column": lang_select_language_column,
                "lang_select_return_known": lang_select_return_known,
                "lang_select_lh_config": lang_select_lh_config,
                "lang_select_local_config": lang_select_local_config,
                "lang_select_s3_config": lang_select_s3_config,
           },
            exec_script_name=EXEC_SCRIPT_NAME,
            server_url=server_url,
            prefix=PREFIX,
        )
        ComponentUtils.add_settings_to_component(execute_job, ONE_WEEK_SEC)
        ComponentUtils.set_s3_env_vars_to_component(execute_job, s3_access_secret)
        ComponentUtils.set_s3_env_vars_to_component(execute_job, lang_select_s3_access_secret, prefix=PREFIX)
        execute_job.after(ray_cluster)

    # set image pull secrets
    dsl.get_pipeline_conf().set_image_pull_secrets([k8s_client.V1ObjectReference(name="prod-all-icr-io")])
    # Configure the pipeline level to one week (in seconds)
    dsl.get_pipeline_conf().set_timeout(ONE_WEEK_SEC)


if __name__ == "__main__":
    # Compiling the pipeline
    compiler.Compiler().compile(lang_select, __file__.replace(".py", ".yaml"))
