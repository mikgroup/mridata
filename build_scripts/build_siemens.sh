#! /usr/bin/env bash

apt-get install -y xsdcxx libxerces-c-dev h5utils hdf5-tools libtinyxml-dev libxml2-dev libxslt1-dev
git clone https://github.com/ismrmrd/siemens_to_ismrmrd.git
cd siemens_to_ismrmrd
mkdir build
cd build
cmake ..
make
make install
cd ../../
rm -rf siemens_to_ismrmrd
