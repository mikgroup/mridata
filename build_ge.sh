#! /usr/bin/env bash

# GE to ISMRMRD
if [ -d "orchestra-sdk-1.6-1/lib" ]; then
    git clone https://github.com/frankong/ge_to_ismrmrd.git
    cd ge_to_ismrmrd && \
	mkdir build && \
	cd build && \
	cmake -D OX_INSTALL_DIRECTORY=$SDKTOP .. && \
	make && \
	sudo make install && \
	cd ../..
fi
