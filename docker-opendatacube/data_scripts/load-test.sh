#!/bin/bash

INSTALL_DIR=/opt/opendatacube

# Add product metadata
datacube -v system init
datacube product add $INSTALL_DIR/docs/config_samples/dataset_types/ls_usgs.yaml
jupyter notebook --allow-root --ip="*" --NotebookApp.token=''
