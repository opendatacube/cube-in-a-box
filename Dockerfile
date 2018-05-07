FROM opendatacube/jupyter

USER root

RUN pip3 install matplotlib click scikit-image

USER $NB_UID

WORKDIR /notebooks

CMD jupyter notebook
