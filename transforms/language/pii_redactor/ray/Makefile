# Define the root of the local git clone for the common rules to be able 
# know where they are running from.
REPOROOT=../../../..
# Include a library of common .transform.* targets which most
# transforms should be able to reuse.  However, feel free
# to override/redefine the rules below. 

include $(REPOROOT)/transforms/.make.transforms

TRANSFORM_NAME=pii_redactor

BASE_IMAGE=${RAY_BASE_IMAGE}
venv::	.transforms.ray-venv

test::	.transforms.ray-test

clean:: .transforms.clean

image:: .transforms.ray-image

test-src:: .transforms.test-src

setup:: .transforms.setup

#test-image:: .transforms.ray-test-image
test-image::
	@echo "Skip... do nothing! pushing CI/CD over a cliff with OSError on text_encoder "
	
build:: build-dist image

publish: publish-image

publish-image:: .transforms.publish-image-ray

setup:: .transforms.setup

# set the version of python transform that this depends on.
set-versions: 
	$(MAKE) TRANSFORM_PYTHON_VERSION=${PII_REDACTOR_PYTHON_VERSION} TOML_VERSION=$(PII_REDACTOR_PYTHON_VERSION) .transforms.set-versions
        
build-dist:: set-versions .defaults.build-dist 

publish-dist:: .defaults.publish-dist

run-cli-sample: .transforms.run-cli-ray-sample

run-local-sample: .transforms.run-local-ray-sample

run-s3-sample: .transforms.run-s3-ray-sample

minio-start:	.minio-start

kind-load-image:: .transforms.kind-load-image

docker-load-image: .defaults.docker-load-image

docker-save-image: .defaults.docker-save-image
