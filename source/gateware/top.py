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

# lite-scope debugger
from litescope import LiteScopeAnalyzer

# samples
from gateware.hello import Hello
from gateware.ticker import *
from gateware.random import *

# Platform---------------------------------------------------------------------
# For xc3sprog programmer use 'xc3sprog'
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
                 eth0_clock, eth1_clock, eth2_clock, eth3_clock):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys2x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()

        self.clock_domains.cd_eth0      = ClockDomain()
        self.clock_domains.cd_eth1      = ClockDomain()
        self.clock_domains.cd_eth2      = ClockDomain()
        self.clock_domains.cd_eth3      = ClockDomain()

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
        self.comb += self.cd_eth3.clk.eq(eth3_clock.ref_clk)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)

# BaseSoC ---------------------------------------------------------------------
class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):

        # Timer ---------------------------------------------------------------
        # If timer0 is enabled ensure that update timer is available also
        if "with_timer" in kwargs:
            with_timer = kwargs.get("with_timer")
            if with_timer:
                kwargs["timer_uptime"] = True

        self.platform = Platform

        # SoCCore -------------------------------------------------------------
        SoCCore.__init__(self, self.platform, clk_freq=sys_clk_freq, **kwargs)

        #self.mem_map = {**self.mem_map, **{
        #    "spiflash": 0xd0_000_000
        #}}

        # CRG -----------------------------------------------------------------
        eth0_clock = self.platform.request("eth_clocks_ext", 0)
        eth1_clock = self.platform.request("eth_clocks_ext", 1)
        eth2_clock = self.platform.request("eth_clocks_ext", 2)
        eth3_clock = self.platform.request("eth_clocks_ext", 3)
        self.submodules.crg = _CRG(self.platform, sys_clk_freq,
                                   eth0_clock, eth1_clock,
                                   eth2_clock, eth3_clock)

        # DDR3 SDRAM ----------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(self.platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq)
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
        self.add_spi_sdcard(name="spisdcard", spi_clk_freq=400e3)

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

        # Ethernet interface 0 (used for TFTP boot).
        # Name it "ethphy" and "ethmac" to be recognized by
        # BIOS for tftp boot option. Also if it is the only
        # interface in the system you MUST remove the 'phy_cd'
        # attribute from add_ethernet (or set it to "eth") otherwise
        # build fails. When using external ref_clock set clock_pads
        # to None and provide a clock domain name for the external
        # clock via refclk_cd.
        self.submodules.ethphy = LiteEthPHYRMII(
            clock_pads = None,
            pads       = self.platform.request("eth", 0),
            with_hw_init_reset=True, refclk_cd="eth0")
        self.add_csr("ethphy")
        self.add_ethernet(name="ethmac", phy=self.ethphy, phy_cd="ethphy_eth")

        # Ethernet interface 1
        self.submodules.ethphy1 = LiteEthPHYRMII(
            clock_pads = None,
            pads       = self.platform.request("eth", 1),
            with_hw_init_reset=True, refclk_cd="eth1")
        self.add_csr("ethphy1")
        self.add_ethernet(name="ethmac1", phy=self.ethphy1, phy_cd="ethphy1_eth")

        # Ethernet interface 2
        self.submodules.ethphy2 = LiteEthPHYRMII(
            clock_pads = None,
            pads       = self.platform.request("eth", 2),
            with_hw_init_reset=True, refclk_cd="eth2")
        self.add_csr("ethphy2")
        self.add_ethernet(name="ethmac2", phy=self.ethphy2, phy_cd="ethphy2_eth")

        # Ethernet interface 3
        self.submodules.ethphy3 = LiteEthPHYRMII(
            clock_pads = None,
            pads       = self.platform.request("eth", 3),
            with_hw_init_reset=True, refclk_cd="eth3")
        self.add_csr("ethphy3")
        # Disabled becaused used for etherbone down below
        #self.add_ethernet(name="ethmac3", phy=self.ethphy3, phy_cd="ethphy3_eth")

        # ticker --------------------------------------------------------------
        self.submodules.ticker = Ticker(CLK_FRQ_HZ=sys_clk_freq)
        self.csr.add("ticker")

        # random --------------------------------------------------------------
        self.submodules.random = Random()
        self.csr.add("random")

        # lite-scope debugger -------------------------------------------------
        self.add_etherbone(
            phy         = self.ethphy3,
            phy_cd      = "ethphy3_eth",
            ip_address  = "10.0.0.42",
            mac_address = 0x10e2d5000001,
            udp_port    = 4711
        )

        # CPU signals
        analyzer_signals = [
            self.cpu.ibus.stb,
            self.cpu.ibus.cyc,
            self.cpu.ibus.adr,
            self.cpu.ibus.we,
            self.cpu.ibus.ack,
            self.cpu.ibus.sel,
            self.cpu.ibus.dat_w,
            self.cpu.ibus.dat_r
        ]

        self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
            depth        = 512,
            clock_domain = "sys",
            csr_csv      = "analyzer.csv")
        self.add_csr("analyzer")

