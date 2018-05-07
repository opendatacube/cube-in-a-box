FROM opendatacube/jupyter

USER root

RUN pip3 install matplotlib click scikit-image pep8

USER $NB_UID

WORKDIR /notebooks

CMD jupyter notebook
