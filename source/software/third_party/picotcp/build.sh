#!/bin/bash

export $(cat ../../../../build/software/include/generated/variables.mak | grep 'TRIPLE=')
export CROSS_COMPILE="${TRIPLE}-"
export "$(cat ../../../../build/software/include/generated/variables.mak | grep 'CPUFLAGS=')"
export "$(cat ../../../../build/software/include/generated/variables.mak | grep 'CPU=')"

cd ./picotcp
make clean
make \
	ARCH=${CPU} \
	TAP=0 \
	TUN=0

