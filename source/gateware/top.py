import argparse

from migen import *

from gateware import arty_s7
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.cores.pwm import PWM
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

# Platform---------------------------------------------------------------------
Platform = arty_s7.Platform(programmer='openocd')

# Helpers ---------------------------------------------------------------------
def platform_request_all(platform, name):
    from litex.build.generic_platform import ConstraintError
    r = []
    while True:
        try:
            r += [platform.request(name, len(r))]
        except ConstraintError:
            break
    if r == []:
        raise ValueError
    return r

# CRG -------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform, sys_clk_freq,
                 eth0_clock, eth1_clock, eth2_clock):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys2x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()
        self.clock_domains.cd_eth0      = ClockDomain()
        self.clock_domains.cd_eth1      = ClockDomain()
        self.clock_domains.cd_eth2      = ClockDomain()

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

        # external eth ref clocks
        self.comb += self.cd_eth0.clk.eq(eth0_clock.ref_clk)
        self.comb += self.cd_eth1.clk.eq(eth1_clock.ref_clk)
        self.comb += self.cd_eth2.clk.eq(eth2_clock.ref_clk)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)

# BaseSoC ---------------------------------------------------------------------
class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        self.platform = Platform

        # SoCCore -------------------------------------------------------------
        SoCCore.__init__(self, self.platform, clk_freq=sys_clk_freq, **kwargs)

        #self.mem_map = {**self.mem_map, **{
        #    "spiflash": 0xd0_000_000
        #}}

        # CRG -----------------------------------------------------------------
        eth0_clock = self.platform.request("eth0_clocks")
        eth1_clock = self.platform.request("eth1_clocks")
        eth2_clock = self.platform.request("eth2_clocks")
        self.submodules.crg = _CRG(self.platform, sys_clk_freq,
                                   eth0_clock, eth1_clock, eth2_clock)

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
        # Disabled due to rom size limitations

        #SPIFLASH_PAGE_SIZE    = 256
        #SPIFLASH_SECTOR_SIZE  = 64 * 1024
        #SPIFLASH_DUMMY_CYCLES = 11

        #self.add_spi_flash(dummy_cycles=SPIFLASH_DUMMY_CYCLES)

        #self.add_constant("SPIFLASH_PAGE_SIZE", SPIFLASH_PAGE_SIZE)
        #self.add_constant("SPIFLASH_SECTOR_SIZE", SPIFLASH_SECTOR_SIZE)
        ## Place firmware in second half of 16MB SPI flash. First half is
        ## used for FPGA bitstream
        #self.add_constant("FLASH_BOOT_ADDRESS", self.mem_map["spiflash"] + 0x800000)

        # SPI SD-Card ---------------------------------------------------------
        self.add_spi_sdcard(name="spisdcard", clk_freq=400e3)

        # Hello World ---------------------------------------------------------
        self.submodules.hello = Hello()
        self.csr.add("hello")

        # GPIO ----------------------------------------------------------------
        #pd = self.platform.request("pmodd")
        #self.submodules.pmodd = GPIOInOut(in_signal=pd, out_signal=pd)
        #self.csr.add("pmodd")

        # Misc GPIO -----------------------------------------------------------
        self.submodules.leds = GPIOOut(Cat(platform_request_all(self.platform, "user_led")))
        self.add_csr("leds")

        rgb_led_pads = self.platform.request("rgb_led", 0)
        for n in "rgb":
            setattr(self.submodules, "rgb_led_{}0".format(n), PWM(getattr(rgb_led_pads, n)))
            self.add_csr("rgb_led_{}0".format(n))

        self.submodules.switches = GPIOIn(Cat(platform_request_all(self.platform, "user_sw")))
        self.add_csr("switches")

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

        # Ethernet interface 0
        # Naming this 'ethphy' and 'ethmac' enables BIOS TFTP boot
        # functionality. This is disabled here by naming it 'ethphy0' and
        # 'ethmac0' as BIOS size wont fit into bitstream ROM. If you want
        # this functionality disable other functions like booting from
        # SD card
        self.submodules.ethphy = LiteEthPHYRMII(
            clock_pads = eth0_clock,
            pads       = self.platform.request("eth0"),
            name="ethphy",
            with_hw_init_reset=True, cd_name="eth0", no_clk_out=True)
        self.add_csr("ethphy")
        self.add_ethernet(name="ethmac", phy=self.ethphy)

        # Ethernet interface 1
        self.submodules.ethphy1 = LiteEthPHYRMII(
            clock_pads = eth1_clock,
            pads       = self.platform.request("eth1"),
            name="ethphy1",
            with_hw_init_reset=True, cd_name="eth1", no_clk_out=True)
        self.add_csr("ethphy1")
        self.add_ethernet(name="ethmac1", phy=self.ethphy1)

        # Ethernet interface 2
        self.submodules.ethphy2 = LiteEthPHYRMII(
            clock_pads = eth2_clock,
            pads       = self.platform.request("eth2"),
            name="ethphy2",
            with_hw_init_reset=True, cd_name="eth2", no_clk_out=True)
        self.add_csr("ethphy2")
        self.add_ethernet(name="ethmac2", phy=self.ethphy2)

