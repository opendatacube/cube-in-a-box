FROM ubuntu:16.04
# This Dockerfile should follow the Travis configuration process
# available here: https://github.com/opendatacube/datacube-core/blob/develop/.travis.yml

# First add the NextGIS repo
RUN apt-get update && apt-get install -y software-properties-common python-software-properties
RUN add-apt-repository ppa:nextgis/ppa

# And now install apt dependencies, including a few of the heavy Python projects
RUN apt-get update && apt-get install -y \
    wget unzip \
    gdal-bin libgdal-dev libgdal20 libudunits2-0 \
    python3 python3-gdal python3-setuptools python3-dev python3-numpy python3-netcdf4

# Get the code, and put it in /opt
WORKDIR /opt
RUN wget "https://github.com/opendatacube/datacube-core/archive/develop.zip" -O /tmp/odc.zip
RUN unzip /tmp/odc.zip
RUN mv /opt/datacube-core-develop /opt/opendatacube

# Install the dependencies
WORKDIR /opt/opendatacube
RUN apt-get install -y python3-pip

ENV LC_ALL C.UTF-8

RUN pip3 install '.[test,analytics,celery,s3]' --upgrade
RUN pip3 install ./tests/drivers/fail_drivers --no-deps --upgrade

RUN python3 setup.py develop

CMD datacube --help
