FROM opendatacube/datacube-jupyter:latest

USER root

# Get more dependencies
RUN pip3 install \
    scikit-image \
    && rm -rf $HOME/.cache/pip

# Switch back to unprivileged user
USER $NB_UID
