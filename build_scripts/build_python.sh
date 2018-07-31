#! /usr/bin/env bash

wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh

bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda

pip install \
    setuptools \
    django \
    h5py  \
    psycopg2 \
    boto3 \
    pillow \
    celery \
    django-filter \
    django-storages \
    pyxb \
    django-el-pagination \
    django-registration-redux \
    redis \
    pycurl
    
# ISMRMRD-python
git clone https://github.com/ismrmrd/ismrmrd-python.git
cd ismrmrd-python
python setup.py install
