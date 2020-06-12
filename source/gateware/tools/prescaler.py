from math import ceil, log2
from migen import *


class Prescaler(Module):

    def __init__(self, sys_clk=None, CLK_FRQ_HZ=100_000_000, OUT_FRQ_HZ=1):

        self.ready = Signal()
        self.clk_out = Signal()

        ###

        MAX_COUNTER = (CLK_FRQ_HZ / (OUT_FRQ_HZ * 2))
        COUNTER_WIDTH = ceil(log2(MAX_COUNTER + 1))
        self.counter = Signal(COUNTER_WIDTH)
        self.clk_out_ = Signal()


        # In case of more then one clock domain, the sys clock is NOT
        # attached per default. So do it here. Only needed when module
        # is top level.
        if isinstance(sys_clk, Signal):
            self.clock_domains.cd_sys = ClockDomain("sys", reset_less=True)
            self.comb += self.cd_sys.clk.eq(sys_clk)


        self.comb += [
            self.clk_out.eq(self.clk_out_)
        ]

        self.sync += [
            If(self.ready,
                If(self.counter == 0,
                    self.counter.eq(int(MAX_COUNTER)),
                    self.clk_out_.eq(~self.clk_out_)
                ).Else(
                    self.counter.eq(self.counter - 1)
                )
            ).Else(
                self.ready.eq(1),
                self.counter.eq(int(MAX_COUNTER)),
                self.clk_out_.eq(0)
            )
        ]

