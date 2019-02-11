FROM opendatacube/jupyter

USER root

RUN apt-get -y update && apt-get install -y graphviz

RUN pip3 install matplotlib click scikit-image pep8 ruamel.yaml dask distributed graphviz

RUN apt-get update && apt-get install -y graphviz

USER $NB_UID

WORKDIR /notebooks

CMD jupyter notebook
