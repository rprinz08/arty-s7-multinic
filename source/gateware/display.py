from litex.soc.interconnect.csr import *
from gateware.disp7.display import *


class Disp7_stub(Module, AutoCSR):

    def __init__(self, port,
                 sys_clk=None, CLK_FRQ_HZ=100_000_000,
                 REFRESH_CLK_HZ=100, NUM_DIGITS=2,
                 BCD_MODE=False, FLIP=False):

        self.dispval = dispval = CSRStorage(NUM_DIGITS * 4)

        ###

        # In case of more then one clock domain, the sys clock is NOT
        # attached per default. So do it here. Only needed when module
        # is top level.
        if isinstance(sys_clk, Signal):
            self.clock_domains.cd_sys = ClockDomain("sys", reset_less=True)
            self.comb += self.cd_sys.clk.eq(sys_clk)

        # Create 7segment display.
        self.submodules.disp1 = disp1 = Disp7(sys_clk=sys_clk,
                                             CLK_FRQ_HZ=CLK_FRQ_HZ,
                                             REFRESH_CLK_HZ=250, NUM_DIGITS=2,
                                             BCD_MODE=False, FLIP=True)

        # Join combinatorial signals.
        self.comb += [
            disp1.dispval.eq(dispval.storage),
            port.eq(Cat(disp1.port, disp1.seg_en[0]))
        ]

