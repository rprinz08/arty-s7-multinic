from migen import *


class Disp7_digit(Module):

    def __init__(self, sys_clk=None, ENABLE_HEX=False, FLIP=False):

        ALL_OFF = 0b1111111
        self._hex = ENABLE_HEX
        self._flip = FLIP

        self.dispval = value = Signal(4)
        self.segments = segments = Signal(7)

        ###

        # In case of more then one clock domain, the sys clock is NOT
        # attached per default. So do it here. Only needed when module
        # is top level.
        if isinstance(sys_clk, Signal):
            self.clock_domains.cd_sys = ClockDomain("sys", reset_less=True)
            self.comb += self.cd_sys.clk.eq(sys_clk)


        if ENABLE_HEX:
            if FLIP:

                self.comb += [ Case(value,
                    {
                         0: segments.eq(0b1000000),
                         1: segments.eq(0b1001111),
                         2: segments.eq(0b0100100),
                         3: segments.eq(0b0000110),
                         4: segments.eq(0b0001011),
                         5: segments.eq(0b0010010),
                         6: segments.eq(0b0010000),
                         7: segments.eq(0b1000111),
                         8: segments.eq(0b0000000),
                         9: segments.eq(0b0000010),

                        10: segments.eq(0b0000001),
                        11: segments.eq(0b0011000),
                        12: segments.eq(0b1110000),
                        13: segments.eq(0b0001100),
                        14: segments.eq(0b0110000),
                        15: segments.eq(0b0110001),

                        "default": self.segments.eq(ALL_OFF)
                    })
                ]
            else:
                self.comb += [ Case(value,
                    {
                         0: segments.eq(0b1000000),
                         1: segments.eq(0b1111001),
                         2: segments.eq(0b0100100),
                         3: segments.eq(0b0110000),
                         4: segments.eq(0b0011001),
                         5: segments.eq(0b0010010),
                         6: segments.eq(0b0000010),
                         7: segments.eq(0b1111000),
                         8: segments.eq(0b0000000),
                         9: segments.eq(0b0010000),

                        10: segments.eq(0b0001000),
                        11: segments.eq(0b0000011),
                        12: segments.eq(0b1000110),
                        13: segments.eq(0b0100001),
                        14: segments.eq(0b0000110),
                        15: segments.eq(0b0001110),

                        "default": self.segments.eq(ALL_OFF)
                    })
                ]
        else:
            if FLIP:
                self.comb += [ Case(value,
                    {
                         0: segments.eq(0b1000000),
                         1: segments.eq(0b1001111),
                         2: segments.eq(0b0100100),
                         3: segments.eq(0b0000110),
                         4: segments.eq(0b0001011),
                         5: segments.eq(0b0010010),
                         6: segments.eq(0b0010000),
                         7: segments.eq(0b1000111),
                         8: segments.eq(0b0000000),
                         9: segments.eq(0b0000010),

                        "default": self.segments.eq(ALL_OFF)
                    })
                ]
            else:
                self.comb += [ Case(value,
                    {
                         0: segments.eq(0b1000000),
                         1: segments.eq(0b1111001),
                         2: segments.eq(0b0100100),
                         3: segments.eq(0b0110000),
                         4: segments.eq(0b0011001),
                         5: segments.eq(0b0010010),
                         6: segments.eq(0b0000010),
                         7: segments.eq(0b1111000),
                         8: segments.eq(0b0000000),
                         9: segments.eq(0b0010000),

                        "default": self.segments.eq(ALL_OFF)
                    })
                ]


    @property
    def hex(self):
        return self._hex

    @property
    def flip(self):
        return self._flip

