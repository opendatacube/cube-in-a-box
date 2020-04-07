ARG py_env_path=/env

# Basically env_builder stage should not need to change from service to service
#   only change content of requirement.txt
#  1. Copy requirements.txt
#  2. Download/compile/re-use all the wheels
#  3. Build environment from wheels
FROM opendatacube/geobase:wheels as env_builder

RUN mkdir -p /conf
COPY requirements.txt /conf/
RUN env-build-tool wheels /conf/requirements.txt /wheels
ARG py_env_path
RUN env-build-tool new /conf/requirements.txt ${py_env_path} /wheels

#--------------------------------------------------------------------------------
# Runner stage might need changing if extra Ubuntu packages are needed for
# different purposes
# --------------------------------------------------------------------------------
FROM opendatacube/geobase:runner
ARG py_env_path

# Copy python env, tini
COPY --from=env_builder $py_env_path $py_env_path
COPY --from=env_builder /bin/tini /bin/tini

# This step might require customization
RUN apt-get update -y \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing --no-install-recommends \
  # developer convenience
  postgresql-client-10 \
  less \
  vim \
  git \
  && rm -rf /var/lib/apt/lists/*

COPY with_bootstrap /bin/
ENV LC_ALL=C.UTF-8 \
    PATH="$py_env_path/bin:$PATH"

RUN pip3 install git+https://github.com/sat-utils/sat-search.git@0.3.0-b2

RUN useradd -m -s /bin/bash -N dcuser
USER dcuser

ENTRYPOINT ["/bin/tini", "-s", "--", "with_bootstrap"]
