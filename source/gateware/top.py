#import sys
#sys.path.insert(0,'..')

import argparse

from migen import *

from gateware import arty_s7
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from liteeth.phy.rmii import LiteEthPHYRMII
from litex.soc.cores.spi_flash import *
from litex.soc.cores.gpio import *

# hello world sample
from gateware.hello import Hello

# Seven Segment Display
from gateware.display import Disp7_stub

# Platform---------------------------------------------------------------------
Platform = arty_s7.Platform(programmer='openocd')

# CRG -------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys2x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()
        self.clock_domains.cd_eth       = ClockDomain()

        # # #

        cpu_reset = platform.request("cpu_reset")
        clk100 = platform.request("clk100")

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~cpu_reset)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys2x,     2*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200,    200e6)
        pll.create_clkout(self.cd_eth,       50e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)

# BaseSoC ---------------------------------------------------------------------
class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        self.platform = Platform

        # SoCCore -------------------------------------------------------------
        SoCCore.__init__(self, self.platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG -----------------------------------------------------------------
        self.submodules.crg = _CRG(self.platform, sys_clk_freq)

        self.mem_map = {**self.mem_map, **{
            "spiflash": 0xd0000000
        }}

        # DDR3 SDRAM ----------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(self.platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq,
                interface_type = "MEMORY")
            self.add_csr("ddrphy")
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MT41K128M16(sys_clk_freq, "1:4"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # SPI Flash -----------------------------------------------------------
        SPIFLASH_PAGE_SIZE    = 256
        SPIFLASH_SECTOR_SIZE  = 64 * 1024
        SPIFLASH_DUMMY_CYCLES = 11

        self.add_spi_flash(dummy_cycles=SPIFLASH_DUMMY_CYCLES)

        self.add_constant("SPIFLASH_PAGE_SIZE", SPIFLASH_PAGE_SIZE)
        self.add_constant("SPIFLASH_SECTOR_SIZE", SPIFLASH_SECTOR_SIZE)
        # Place firmware in second half of 16MB SPI flash. First half is
        # used for FPGA bitstream
        self.add_constant("FLASH_BOOT_ADDRESS", self.mem_map["spiflash"] + 0x800000)

        # SPI SD-Card ---------------------------------------------------------
        self.add_spi_sdcard(name="spisdcard", clk_freq=400e3)

        # Hello World ---------------------------------------------------------
        self.submodules.hello = Hello()
        self.csr.add("hello")

        # GPIO ----------------------------------------------------------------
        #pd = self.platform.request("pmodd")
        #self.submodules.pmodd = GPIOInOut(in_signal=pd, out_signal=pd)
        #self.csr.add("pmodd")

        # Seven Segment Display -----------------------------------------------
        pc = self.platform.request("pmodc")
        self.submodules.disp7 = Disp7_stub(pc,
                                           CLK_FRQ_HZ=sys_clk_freq,
                                           REFRESH_CLK_HZ=250, NUM_DIGITS=2,
                                           BCD_MODE=False, FLIP=True)
        self.csr.add("disp7")

        # Ethernet ------------------------------------------------------------
        # Loval IP4 address of Ethernet interface 1 (10.0.0.50)
        self.add_constant("LOCALIP1", 10)
        self.add_constant("LOCALIP2", 0)
        self.add_constant("LOCALIP3", 0)
        self.add_constant("LOCALIP4", 50)

        # IP4 Address of TFTP boot server (10.0.0.100)
        self.add_constant("REMOTEIP1", 10)
        self.add_constant("REMOTEIP2", 0)
        self.add_constant("REMOTEIP3", 0)
        self.add_constant("REMOTEIP4", 100)

        eth_clocks = self.platform.request("eth_clocks")

        # Ethernet interface 0
        # Naming this 'ethphy' and 'ethmac' enables BIOS TFTP boot
        # functionality. This is disabled here by naming it 'ethphy0' and
        # 'ethmac0' as BIOS size wont fit into bitstream ROM. If you want
        # this functionality disable other functions like booting from
        # SD card
        self.submodules.ethphy0 = LiteEthPHYRMII(
            clock_pads = eth_clocks,
            pads       = self.platform.request("eth0"),
            name="ethphy0",
            with_hw_init_reset=True, cd_name="eth", no_clk_out=True)
        self.add_csr("ethphy0")
        self.add_ethernet(name="ethmac0", phy=self.ethphy0)

        # Ethernet interface 1
        self.submodules.ethphy1 = LiteEthPHYRMII(
            clock_pads = eth_clocks,
            pads       = self.platform.request("eth1"),
            name="ethphy1",
            with_hw_init_reset=True, cd_name="eth", no_clk_out=True)
        self.add_csr("ethphy1")
        self.add_ethernet(name="ethmac1", phy=self.ethphy1)

