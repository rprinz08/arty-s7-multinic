#!/usr/bin/env python3

from os import path
import argparse
import logging

from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from source.top import *


def build(args):
    """ Convert migen to HDL and optionally build bitsreami and BIOS """
    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))

    print("*** BUILDING BITSTREAM")
    builder.build(**vivado_build_argdict(args))
    print("*** BUILD DONE")


def load(args):
    """ Temporarily load bitsream into device """
    logging.disable(level=logging.CRITICAL)
    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))

    # Using xc3sprog is faster than using Vivado to load a bitstream to FPGA.
    # So use xc3sprog for loading and Vivado for flashing.
    # Uncomment next line to use xc3sprog for loading or change
    # platform in top.py
    #soc.platform.programmer = 'xc3sprog'

    bitstream = path.join(builder.gateware_dir, 'top.bit')

    print("*** LOADING BITSTREAM (%s) INTO FPGA" % bitstream)
    prog = soc.platform.create_programmer()
    prog.load_bitstream(bitstream)
    print("*** LOAD DONE")


def flash(args):
    """ Permanent program bitstream into configuration flash """
    logging.disable(level=logging.CRITICAL)
    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))

    # To flash a bitstream permanently to config flash, use Vivado as it
    # includes everything needed. When using xc3sprog an additional flash
    # proxy is needed. See additional comments in arty_s7.py
    #soc.platform.programmer = 'vivado'
    bitstream = path.join(builder.gateware_dir, 'top.bin')

    print("*** FLASHING BITSTREAM (%s) TO FPGA FLASH" % bitstream)
    prog = soc.platform.create_programmer()
    prog.flash(0, bitstream)
    print("*** FLASH DONE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LiteX SoC make")
    parser.add_argument('command', nargs=1, help='Command to perform',
                        choices=['build', 'conv', 'load',
                                 'flash'],
                        default='build')
    builder_args(parser)

    if 'build' in sys.argv:
        soc_sdram_args(parser) # includes soc_core_args
        vivado_build_args(parser)
    elif 'conv' in sys.argv:
        soc_sdram_args(parser)
        vivado_build_args(parser)
        if not '--no-compile-software' in sys.argv:
            sys.argv.append('--no-compile-software')
        if not '--no-compile-gateware' in sys.argv:
            sys.argv.append('--no-compile-gateware')

    args = parser.parse_args()

    if args.command[0] == 'build':
        build(args)
    elif args.command[0] == 'conv':
        build(args)
    elif args.command[0] == 'load':
        load(args)
    elif args.command[0] == 'flash':
        flash(args)
    else:
        parser.print_help()

