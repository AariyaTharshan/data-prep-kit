ARG BASE_IMAGE=docker.io/rayproject/ray:2.24.0-py310

FROM ${BASE_IMAGE}

RUN pip install --upgrade --no-cache-dir pip 

# Install pytest so we can test the image later
RUN pip install --no-cache-dir pytest

# Copy and install data processing libraries
# These are expected to be placed in the docker context before this is run (see the make image).
COPY --chown=ray:users data-processing-lib-python/ data-processing-lib-python/
RUN cd data-processing-lib-python && pip install --no-cache-dir -e .
COPY --chown=ray:users data-processing-lib-ray/ data-processing-lib-ray/
RUN cd data-processing-lib-ray    && pip install --no-cache-dir -e .
COPY --chown=ray:users python-transform/  python-transform/
RUN cd python-transform && pip install --no-cache-dir -e .

COPY --chown=ray:users src/ src/
COPY --chown=ray:users pyproject.toml pyproject.toml
RUN pip install --no-cache-dir -e .

# copy the main() entry point to the image 
COPY ./src/resize_transform_ray.py ./

# copy some of the samples in
COPY ./src/resize_local_ray.py local/

COPY test/ test/
COPY test-data/ test-data/

USER root
RUN chown -R ray /home/ray/test
RUN chown -R ray /home/ray/test-data
USER ray

ENV PYTHONPATH /home/ray

# Put these at the end since they seem to upset the docker cache.
ARG BUILD_DATE
ARG GIT_COMMIT
LABEL build-date=$BUILD_DATE
LABEL git-commit=$GIT_COMMIT
