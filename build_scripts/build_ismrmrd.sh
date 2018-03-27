#! /usr/bin/env bash

# ISMRMRD
apt-get update \
    && apt-get install -y \
	       build-essential \
	       fftw-dev \
	       g++ \
	       libhdf5-serial-dev \
	       h5utils \
	       hdf5-tools \
	       libboost-all-dev \
	       xsdcxx \
	       libtinyxml-dev \
	       libxslt1-dev \
	       libxml2-dev \
	       libxerces-c-dev \
	       cmake \
	       git \
	       sudo

git clone https://github.com/ismrmrd/ismrmrd.git
cd ismrmrd
mkdir build
cd build
cmake ..
make
sudo make install
