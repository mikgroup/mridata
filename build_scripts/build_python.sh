#! /usr/bin/env bash

export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"

wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.3.21-Linux-x86_64.sh

bash Miniconda3-4.3.21-Linux-x86_64.sh -b -p /miniconda

pip install --upgrade pip

pip install \
    boto3 \
    celery \
    Django \
    django-el-pagination \
    django-filter \
    django-registration-redux \
    django-s3direct \
    django-storages \
    h5py \
    numpy \
    Pillow \
    psycopg2 \
    pycurl \
    PyXB \
    redis \
    django-taggit \
    django-widget-tweaks \
    django-crispy-forms \
    django-bootstrap3
# ISMRMRD-python
git clone https://github.com/ismrmrd/ismrmrd-python.git
cd ismrmrd-python
python setup.py install
