#! /usr/bin/env bash

apt-get install -y wget

wget --quiet https://repo.continuum.io/miniconda/Miniconda3-py39_4.9.2-Linux-x86_64.sh

bash Miniconda3-py39_4.9.2-Linux-x86_64.sh -b -p /miniconda

pip install --upgrade pip

pip install -r build_scripts/requirements.txt
