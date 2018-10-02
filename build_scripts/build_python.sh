#! /usr/bin/env bash

export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"

wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.3.21-Linux-x86_64.sh

bash Miniconda3-4.3.21-Linux-x86_64.sh -b -p /miniconda

pip install \
    boto3==1.7.66 \
    celery==4.2.1 \
    Django==1.11.3 \
    django-el-pagination==3.2.4 \
    django-filter==1.0.4 \
    django-registration-redux==1.8 \
    django-s3direct==1.0.2 \
    django-storages==1.6.6 \
    h5py==2.8.0 \
    numpy==1.15.0 \
    Pillow==5.2.0 \
    psycopg2==2.7.5 \
    pycurl==7.43.0.2 \
    PyXB==1.2.6 \
    redis==2.10.6
    
# ISMRMRD-python
git clone https://github.com/ismrmrd/ismrmrd-python.git
cd ismrmrd-python
python setup.py install
