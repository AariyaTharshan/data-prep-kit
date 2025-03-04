# Define the root of the local git clone for the common rules to be able 
# know where they are running from.
REPOROOT=../../../..
# Include a library of common .transform.* targets which most
# transforms should be able to reuse.  However, feel free
# to override/redefine the rules below. 

# $(REPOROOT)/.make.versions file contains the versions

TRANSFORM_NAME=pdf2parquet

RUN_ARGS=" --data_local_config \"{ 'input_folder' : '../test-data/input', 'output_folder' : '../output'}\"  \
	--data_files_to_use \"['.pdf','.zip']\" "


include $(REPOROOT)/transforms/.make.transforms

venv::	.transforms.python-venv

test::	.transforms.python-test

clean:: .transforms.clean

image:: .transforms.python-image

test-src:: .transforms.test-src

setup:: .transforms.setup

build:: build-dist image

publish: publish-image

publish-image:: .transforms.publish-image-python

setup:: .transforms.setup

# distribution versions is the same as image version.
set-versions:
	$(MAKE) TRANSFORM_PYTHON_VERSION=$(PDF2PARQUET_PYTHON_VERSION) TOML_VERSION=$(PDF2PARQUET_PYTHON_VERSION) .transforms.set-versions 
        
build-dist:: .defaults.build-dist 

publish-dist:: .defaults.publish-dist

test-image:: .transforms.python-test-image

run-cli-sample: .transforms.run-cli-python-sample
	$(MAKE) RUN_FILE=$(TRANSFORM_NAME)_transform_python.py \
            RUN_ARGS=" --data_local_config \"{ 'input_folder' : '../test-data/input', 'output_folder' : '../output'}\"  \
				--data_files_to_use \"['.pdf','.zip']\" " \
            .transforms.run-src-file

run-local-sample: .transforms.run-local-sample

run-local-python-sample: .transforms.run-local-python-sample

#run-s3-ray-sample: .transforms.run-s3-ray-sample

minio-start:	.minio-start

kind-load-image:: .transforms.kind-load-image

docker-load-image: .defaults.docker-load-image

docker-save-image: .defaults.docker-save-image
