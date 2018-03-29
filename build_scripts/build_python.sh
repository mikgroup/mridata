#! /usr/bin/env bash

pip install django \
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
