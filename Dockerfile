
FROM opendatacube/geobase:wheels as env_builder

ARG py_env_path=/env

RUN mkdir -p /conf
COPY requirements.txt /conf/
RUN env-build-tool wheels /conf/requirements.txt /wheels
ARG py_env_path
RUN env-build-tool new /conf/requirements.txt ${py_env_path} /wheels

FROM opendatacube/geobase:runner
ARG py_env_path

COPY --from=env_builder $py_env_path $py_env_path
COPY --from=env_builder /bin/tini /bin/tini

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

CMD ["jupyter", "notebook", "--allow-root", "--ip='0.0.0.0'" "--NotebookApp.token='secretpassword'"]