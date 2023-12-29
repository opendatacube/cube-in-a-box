FROM osgeo/gdal:ubuntu-small-3.6.3

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    TINI_VERSION=v0.19.0

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN apt-get update && \
    apt-get install -y \
      build-essential \
      git \
      # For Psycopg2
      libpq-dev python3-dev \
      python3-pip \
      python3-wheel \
      wget \
    && apt-get autoclean \
    && apt-get autoremove \
    && rm -rf /var/lib/{apt,dpkg,cache,log}

COPY requirements.txt /conf/
COPY products.csv /conf/
COPY cuborizonte /cuborizonte

RUN pip3 install --no-cache-dir --requirement /conf/requirements.txt

WORKDIR /notebooks

ENTRYPOINT ["/tini", "--"]

CMD ["/bin/sh", "-c", "\
    jupyter notebook --allow-root --ip='0.0.0.0' --NotebookApp.token='secretpassword' & \
    python /cuborizonte/divide_bands.py /cuborizonte/data/aerial_1999 /cuborizonte/data/aerial_1999_processed && \
    python /cuborizonte/build_dataset.py /cuborizonte/data/aerial_1999_processed /cuborizonte/data/aerial_1999 aerial_image_1999 && \
    python /cuborizonte/indexer.py /cuborizonte/data/aerial_1999_processed"]



