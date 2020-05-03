from migen import *
from pprint import pprint


class BinToBCDDigit(Module):

    def __init__(self, sys_clk=None, CLK_FRQ_HZ=100_000_000):

        self.ready = ready = Signal()   # out
        self.ena = ena = Signal()       # in
        self.binary = binary = Signal() # in
        self.c_out = c_out = Signal()   # out
        self.bcd = bcd = Signal(4)      # out

        ###

        # keeps track of the previous enable to identify when enabled
        # is first asserted
        self.prev_ena = prev_ena = Signal()


        # In case of more then one clock domain, the sys clock is NOT
        # attached per default. So do it here. Only needed when module
        # is top level.
        if isinstance(sys_clk, Signal):
            self.clock_domains.cd_sys = ClockDomain("sys", reset_less=True)
            self.comb += self.cd_sys.clk.eq(sys_clk)


        # assert carry out when register value exceeds 4
        self.comb += c_out.eq(bcd[3] |
                             (bcd[2] & bcd[1]) |
                             (bcd[2] & bcd[0]))


        self.sync += [
            If(ready,
                # keep track of last enable
                prev_ena.eq(ena),
                # if operation activated
                If(ena == 1,
                    # if first cycle of activation
                    If(prev_ena == 0,
                        # initialize the register
                        bcd.eq(0)
                    # else if register value exceeds 4
                    ).Elif(c_out == 1,
                        # shift new bit into first register
                        bcd[0].eq(binary),
                        # set second register to adjusted value
                        bcd[1].eq(~bcd[0]),
                        # set third register to adjusted value
                        bcd[2].eq(~(bcd[1] ^ bcd[0])),
                        # set fourth register to adjusted value
                        bcd[3].eq(bcd[3] & bcd[0])
                    # else register value does not exceed 4
                    ).Else(
                        # shift register values up and shift in new bit
                        bcd.eq(Cat(binary, bcd[0:3]))
                    )
                )
            ).Else(
                ready.eq(1),
                # clear ena history
                prev_ena.eq(0),
                # clear output
                bcd.eq(0)
            )
        ]

