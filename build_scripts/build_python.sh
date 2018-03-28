#! /usr/bin/env bash

pip install django \
    boto3 \
    pillow \
    celery \
    django-filter \
    django-storages \
    django-el-pagination \
    django-registration-redux \
    numpy \
    h5py  \
    pyxb
    
# ISMRMRD-python
git clone https://github.com/ismrmrd/ismrmrd-python.git
cd ismrmrd-python
python setup.py install
