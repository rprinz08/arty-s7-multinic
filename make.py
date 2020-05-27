#!/usr/bin/env python3

import sys
sys.path.insert(0, './source')

import os
import argparse
import logging

from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from gateware.top import *


def build(args):
    """ Convert migen to HDL and optionally build bitsreami and BIOS """
    soc = BaseSoC(**soc_sdram_argdict(args))
    # use minimal bios terminal otherwise bios would not fit in ROM
    builder = Builder(soc, **builder_argdict(args), bios_options = ["TERM_MINI"])

    print("*** BUILDING BITSTREAM")
    kw = {}
    if 'build_name' in args and isinstance(args.build_name, str):
        kw['build_name'] = args.build_name
    builder.build(**vivado_build_argdict(args), **kw)
    print("*** BUILD DONE")


def load(args):
    """ Temporarily load bitsream into device """
    logging.disable(level=logging.CRITICAL)
    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args), bios_options = ["TERM_MINI"])
    bitstream = os.path.join(builder.gateware_dir,
                             '{}.bit'.format(args.build_name))

    print("*** LOADING BITSTREAM (%s) INTO FPGA" % bitstream)
    prog = soc.platform.create_programmer()
    prog.load_bitstream(bitstream)
    print("*** LOAD DONE")


def flash(args):
    """ Permanent program bitstream into configuration flash """
    logging.disable(level=logging.CRITICAL)
    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args), bios_options = ["TERM_MINI"])
    bitstream = os.path.join(builder.gateware_dir,
                             '{}.bit'.format(args.build_name))

    print("*** FLASHING BITSTREAM (%s) TO FPGA FLASH" % bitstream)
    prog = soc.platform.create_programmer()
    prog.flash(0, bitstream)
    print("*** FLASH DONE")


def flash_sw(args):
    logging.disable(level=logging.CRITICAL)
    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args), bios_options = ["TERM_MINI"])

    base = 0x800_000
    firmware = args.firmware
    print("Flashing {} at 0x{:08x}".format(firmware, base))
    prog = builder.soc.platform.create_programmer()
    prog.flash(base, firmware)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LiteX SoC make")
    parser.add_argument('command', nargs=1, help='Command to perform',
                        choices=['build', 'build-sw', 'build-fpga',
                                 'conv',
                                 'load', 'flash', 'flash-sw'],
                        default='build')
    parser.add_argument('--build_name', default='top',
                              help='Name of build')
    builder_args(parser)

    if any(a in sys.argv for a in [
            'build', 'build-sw', 'build-fpga',
            'flash', 'flash-sw',
            'conv']):
        soc_sdram_args(parser) # includes soc_core_args
        vivado_build_args(parser)

    if 'build-sw' in sys.argv:
        while '--no-compile-software' in sys.argv:
            sys.argv.remove('--no-compile-software')
        if not '--no-compile-gateware' in sys.argv:
            sys.argv.append('--no-compile-gateware')

    elif 'build-fpga' in sys.argv:
        while '--no-compile-gateware' in sys.argv:
            sys.argv.remove('--no-compile-gateware')
        if not '--no-compile-software' in sys.argv:
            sys.argv.append('--no-compile-software')

    elif 'conv' in sys.argv:
        if not '--no-compile-software' in sys.argv:
            sys.argv.append('--no-compile-software')
        if not '--no-compile-gateware' in sys.argv:
            sys.argv.append('--no-compile-gateware')

    elif 'flash-sw' in sys.argv:
        parser.add_argument("--firmware", default=None,
            help="Firmware to flash (fbi format)")

    args = parser.parse_args()

    if args.command[0] in ['build', 'build-sw', 'build-fpga', 'conv']:
        build(args)
    elif args.command[0] == 'load':
        load(args)
    elif args.command[0] == 'flash':
        flash(args)
    elif args.command[0] == 'flash-sw':
        flash_sw(args)
    else:
        parser.print_help()

