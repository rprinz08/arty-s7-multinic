from migen import *
from gateware.disp7.bin_to_bcd import *
from gateware.disp7.decoder_7seg import *
from gateware.disp7.prescaler import *
from pprint import pprint


class Disp7(Module):
    """ 7 Segment display driver for 1 to 4 digits.
    REFRESH_CLK_HZ defines the refresh rate between the multiplexed digits.
    NUM_DIGITS     defines the number of digits (1 to 4).
    BCD_MODE       if True show values in decimal else in hexadecimal.
    FLIP           Can be used to flip display top to bottom depending on
                   how it is installed. """

    def __init__(self, sys_clk=None, CLK_FRQ_HZ=100_000_000,
                 REFRESH_CLK_HZ=100, NUM_DIGITS=2,
                 BCD_MODE=False, FLIP=False):

        if NUM_DIGITS < 1 or NUM_DIGITS > 4:
            raise Exception(self.__class__.__name__ +
                            " supports only 1 to 4 digits.")

        self.ready = ready = Signal()
        self.dispval = dispval = Signal(NUM_DIGITS * 4)
        self.port = port = Signal(7)
        self.seg_en = seg_en = Signal(NUM_DIGITS)

        ###

        self.value_int = value_int = Signal(NUM_DIGITS * 4)
        self.value_digit = value_digit = Signal(4)

        # In case of more then one clock domain, the sys clock is NOT
        # attached per default. So do it here. Only needed when module
        # is top level.
        if isinstance(sys_clk, Signal):
            self.clock_domains.cd_sys = ClockDomain("sys", reset_less=True)
            self.comb += self.cd_sys.clk.eq(sys_clk)

        # Create REFRESH_CLK_HZ prescaler for multiplexed display refresh.
        self.submodules.ps_ref = ps_ref = Prescaler(sys_clk=sys_clk,
                                                    CLK_FRQ_HZ=CLK_FRQ_HZ,
                                                    OUT_FRQ_HZ=REFRESH_CLK_HZ)

        # Create 7segment decoder.
        self.submodules.d7 = d7 = Disp7_digit(sys_clk=sys_clk,
                                              ENABLE_HEX=True, FLIP=FLIP)

        # Create clock domain for ps_ref.
        self.clock_domains.cd_ps_ref = ClockDomain("ref_clk", reset_less=True)
        self.comb += self.cd_ps_ref.clk.eq(ps_ref.clk_out)

        if BCD_MODE:
            self.submodules.bin_to_bcd = bin_to_bcd = BinToBCD(sys_clk=sys_clk,
                                                               BITS=NUM_DIGITS*4,
                                                               DIGITS=NUM_DIGITS)
            self.comb += [
                bin_to_bcd.ena.eq(1),
                bin_to_bcd.binary.eq(dispval),
                value_int.eq(bin_to_bcd.bcd)
            ]
        else:
            self.comb += value_int.eq(dispval)

        # Join combinatorial signals.
        self.comb += [
            d7.dispval.eq(value_digit),
            port.eq(d7.segments)
        ]

        # Depending on number of digits select part of display value
        # to show in multiplexed digit selected by enable signal 'seg_en'.
        set_segments = None
        if NUM_DIGITS == 1:
            set_segments = value_digit.eq(value_int[0:4])
        elif NUM_DIGITS == 2:
            if FLIP:
                set_segments = Case(seg_en, {
                    0b10: value_digit.eq(value_int[4:8]),
                    0b01: value_digit.eq(value_int[0:4]) })
            else:
                set_segments = Case(seg_en, {
                    0b10: value_digit.eq(value_int[0:4]),
                    0b01: value_digit.eq(value_int[4:8]) })
        elif NUM_DIGITS == 3:
            if FLIP:
                set_segments = Case(seg_en, {
                    0b100: value_digit.eq(value_int[8:12]),
                    0b010: value_digit.eq(value_int[4:8]),
                    0b001: value_digit.eq(value_int[0:4]) })
            else:
                set_segments = Case(seg_en, {
                    0b100: value_digit.eq(value_int[0:4]),
                    0b010: value_digit.eq(value_int[4:8]),
                    0b001: value_digit.eq(value_int[8:12]) })
        elif NUM_DIGITS == 4:
            if FLIP:
                set_segments = Case(seg_en, {
                    0b1000: value_digit.eq(value_int[12:16]),
                    0b0100: value_digit.eq(value_int[8:12]),
                    0b0010: value_digit.eq(value_int[4:8]),
                    0b0001: value_digit.eq(value_int[0:4]) })
            else:
                set_segments = Case(seg_en, {
                    0b1000: value_digit.eq(value_int[0:4]),
                    0b0100: value_digit.eq(value_int[4:8]),
                    0b0010: value_digit.eq(value_int[8:12]),
                    0b0001: value_digit.eq(value_int[12:16]) })

        select_digit = None
        if NUM_DIGITS > 1:
            # rotate left
            select_digit = seg_en.eq(Cat(seg_en[1:], seg_en[:1]))
            # rotate right
            #select_digit = seg_en.eq(Cat(seg_en[-1:], seg_en[:-1]))
        else:
            select_digit = seg_en.eq(0)

        # Use ps_ref clock domain here for display refresh.
        self.sync.ref_clk += [
            If(ready,
                select_digit,
                set_segments
            ).Else(
                ready.eq(1),
                seg_en.eq(1),
                value_digit.eq(0)
            )
        ]

