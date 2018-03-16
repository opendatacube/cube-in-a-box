#!/bin/bash

INSTALL_DIR=/opt/opendatacube

# Add product metadata
datacube -v system init
datacube product add $INSTALL_DIR/docs/config_samples/dataset_types/ls_usgs.yaml
python3 /datascripts/autoIndex.py -i /home/ubuntu/index-config -o wrs2_asc_desc.shp

jupyter notebook --allow-root --ip="*" --NotebookApp.token=''
