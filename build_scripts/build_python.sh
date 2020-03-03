#! /usr/bin/env bash

export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"

wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.3.21-Linux-x86_64.sh

bash Miniconda3-4.3.21-Linux-x86_64.sh -b -p /miniconda

pip install -r build_scripts/requirements.txt
