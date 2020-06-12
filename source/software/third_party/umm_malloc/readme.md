# UMM Malloc

This directory contains scripts to download and cross-compile
umm_malloc from https://github.com/rhempel/umm_malloc.

1. first build the gateware running `make` in the projects root dir
2. load (`make load`) or flash (`make flash`) the gateware to the FPGA
3. run `get.sh` in this directory to download the umm_malloc source code
4. run `build.sh` to create a cross-compiled library which then can be used by the system firmware
5. goto the firmware directory and build the firmware (`make`) which automatically links the umm_malloc library from here
