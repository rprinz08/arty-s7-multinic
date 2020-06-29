# PicoTCP

This directory contains scripts to download and cross-compile
PicoTCP from

https://github.com/tass-belgium/picotcp

1. first build the gateware running `make` in the projects root dir
2. load (`make load`) or flash (`make flash`) the gateware to the FPGA
3. run `get.sh` in this directory to download the PicoTCP source code
4. patch PicoTCP to support the VexRiscV architecture with `patch.sh`
5. run `build.sh` to create a cross-compiled library which then can be used by
   the system firmware
5. goto the firmware directory and build the firmware (`make`) which automatically
   links the PicoTCP library from here
