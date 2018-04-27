FROM opendatacube/datacube-jupyter:latest

# Get more dependencies
RUN pip3 install \
    scikit-image \
    && rm -rf $HOME/.cache/pip
