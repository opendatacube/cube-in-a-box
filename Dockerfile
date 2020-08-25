
FROM opendatacube/geobase:wheels-3.0.4  as env_builder

ARG py_env_path=/env

RUN mkdir -p /conf
COPY requirements.txt /conf/
RUN env-build-tool new /conf/requirements.txt ${py_env_path} /wheels

FROM opendatacube/geobase:runner-3.0.4
ARG py_env_path

COPY --chown=1000:100 --from=env_builder $py_env_path $py_env_path
COPY --from=env_builder /bin/tini /bin/tini

RUN export GDAL_DATA=$(gdal-config --datadir)
ENV LC_ALL=C.UTF-8 \
    PATH="/env/bin:$PATH"

RUN useradd -m -s /bin/bash -N jovyan -g 100 -u 1000
USER jovyan

WORKDIR /notebooks

ENTRYPOINT ["/bin/tini", "--"]

CMD ["jupyter", "notebook", "--allow-root", "--ip='0.0.0.0'" "--NotebookApp.token='secretpassword'"]
