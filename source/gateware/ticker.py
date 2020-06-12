from migen import *
from litex.soc.interconnect.csr import *
from gateware.tools.prescaler import *


class Ticker(Module, AutoCSR):

    def __init__(self, sys_clk=None, CLK_FRQ_HZ=100_000_000):

        self._ticks = CSRStatus(32)
        self._ms = CSRStatus(32)

        # # #

        # ---------------------------------------------------------------------
        # main clk ticks
        t = Signal(32)

        self.sync += [
            t.eq(t + 1),
            self._ticks.status.eq(t)
        ]

        # ---------------------------------------------------------------------
        # 1ms clk ticks
        t_ms = Signal(32)

        self.submodules.ps_ms = ps_ms = Prescaler(sys_clk=sys_clk,
                                                  CLK_FRQ_HZ=CLK_FRQ_HZ,
                                                  OUT_FRQ_HZ=1000)

        self.clock_domains.cd_ps_ms = ClockDomain("ms_clk", reset_less=True)
        self.comb += self.cd_ps_ms.clk.eq(ps_ms.clk_out)

        self.sync.ms_clk += [
            t_ms.eq(t_ms + 1),
            self._ms.status.eq(t_ms)
        ]

