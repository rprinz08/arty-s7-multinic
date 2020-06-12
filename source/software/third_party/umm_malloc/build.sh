#!/bin/bash

export $(cat ../../../../build/software/include/generated/variables.mak | grep 'TRIPLE=')
export CROSS_COMPILE="${TRIPLE}-"
export "$(cat ../../../../build/software/include/generated/variables.mak | grep 'CPUFLAGS=')"
export "$(cat ../../../../build/software/include/generated/variables.mak | grep 'CPU=')"

cd ./umm_malloc
make -f ../Makefile clean
make -f ../Makefile \
	ARCH=${CPU} \
	CFLAGS="$CPUFLAGS -Itest/support"

