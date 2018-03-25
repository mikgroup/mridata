#! /usr/bin/env bash

# GE to ISMRMRD
if [ -d "orchestra-sdk-1.6-1" ]; then
    git clone https://github.com/frankong/ge_to_ismrmrd.git
    cd ge_to_ismrmrd && \
	mkdir build && \
	cd build && \
	cmake -D OX_INSTALL_DIRECTORY=$SDKTOP -D CXX=g++-4.9 .. && \
	make && \
	sudo make install
fi
