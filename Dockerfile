FROM opendatacube/datacube-core

RUN apt-get update && apt-get install -y ipython ipython-notebook
RUN pip3 install jupyter matplotlib click

WORKDIR /notebooks

CMD jupyter notebook
