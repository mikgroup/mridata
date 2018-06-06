#! /usr/bin/env bash

# ISMRMRD
ls -la /usr/bin | grep gcc

apt-get update
apt-get install -y \
	build-essential \
	fftw-dev \
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
	git

export CC=gcc-4.9
export CXX=g++-4.9

git clone https://github.com/ismrmrd/ismrmrd.git
cd ismrmrd
mkdir build
cd build
cmake ..
make
make install
