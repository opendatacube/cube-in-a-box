#!/bin/bash

# Landsat 7 Collection 1 (Ghana)
echo Fetching Landsat 7 Collection 1 sample data file

FILE=LE071950542015121201T1-SC20170427222707
INSTALL_DIR=/opt/opendatacube

# wget 'http://ec2-52-201-154-0.compute-1.amazonaws.com/datacube/data/LE071950542015121201T1-SC20170427222707.tar.gz' -O /tmp/$FILE.tar.gz

echo Uncompressing sample data
# mkdir -p /data/$FILE

# tar -xzf /tmp/$FILE.tar.gz -C /data/$FILE


# Index & Ingest
echo Adding ODC product
datacube -v product add $INSTALL_DIR/docs/config_samples/dataset_types/ls7_scenes.yaml

echo Running ODC prepare
python3 $INSTALL_DIR/utils/galsprepare.py /data/$FILE/*

echo Indexing data
datacube -v dataset add --auto-match /data/$FILE/*

echo Ingesting data
datacube -v ingest -c /data-scripts/ingest.yml --executor multiproc 2
