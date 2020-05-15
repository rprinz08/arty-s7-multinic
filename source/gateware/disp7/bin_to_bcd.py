from migen import *
from gateware.disp7.bin_to_bcd_digit import *
from pprint import pprint


class BinToBCD(Module):
    """Converts a binary value to a binary-coded-decimal (BCD) value.
    See also: https://johnloomis.org/ece314/notes/devices/binary_to_BCD/bin_to_bcd.html
    """

    def __init__(self, sys_clk=None, CLK_FRQ_HZ=100_000_000,
                 BITS=10, DIGITS=3):

        self.ready = ready = Signal()       # out
        self.ena = ena = Signal()           # in
        self.binary = binary = Signal(BITS) # in
        self.busy = busy = Signal()         # out
        self.bcd = bcd = Signal(DIGITS * 4) # out

        ###

        self.state = state = Signal()
        self.binary_reg = binary_reg = Signal(BITS)
        self.bcd_reg = bcd_reg = Signal(DIGITS * 4)
        self.converter_ena = converter_ena = Signal()
        self.converter_inputs = converter_inputs = Signal(DIGITS + 1)
        self.bit_count = bit_count = Signal(max=BITS+1)


        # In case of more then one clock domain, the sys clock is NOT
        # attached per default. So do it here. Only needed when module
        # is top level.
        if isinstance(sys_clk, Signal):
            self.clock_domains.cd_sys = ClockDomain("sys", reset_less=True)
            self.comb += self.cd_sys.clk.eq(sys_clk)


        digits = []
        for i in range(1, DIGITS+1):
            digit = BinToBCDDigit(sys_clk=sys_clk)
            #self.submodules += digit
            setattr(self.submodules, "digit%s" % i, digit)
            digits.append(digit)
            self.comb += [
                digit.ena.eq(converter_ena),
                digit.binary.eq(converter_inputs[i-1]),
                converter_inputs[i].eq(digit.c_out),
                bcd_reg[i*4-4:i*4].eq(digit.bcd)
            ]


        self.sync += [
            If(ready,
               Case(state, {
                    # idle state
                    # if converter is enabled
                    0: If(ena == 1,
                            # indicate conversion in progress
                            busy.eq(1),
                            # enable the converter
                            converter_ena.eq(1),
                            # latch in binary number for conversion
                            binary_reg.eq(binary),
                            # reset bit counter
                            bit_count.eq(0),
                            # go to convert state
                            state.eq(1)
                       # else converter is not enabled
                       ).Else(
                            # indicate available
                            busy.eq(0),
                            # disable the converter
                            converter_ena.eq(0),
                            # remain in idle state
                            state.eq(0)
                       ),

                    # convert state
                    # if not all bits shifted in
                    1: If(bit_count < BITS + 1,
                            # increment bit counter
                            bit_count.eq(bit_count + 1),
                            # shift next bit into converter
                            converter_inputs[0].eq(binary_reg[BITS-1]),
                            # shift binary number register
                            binary_reg.eq(Cat(0, binary_reg[0:BITS-1])),
                            # remain in convert state
                            state.eq(1)
                       # else all bits shifted in
                       ).Else(
                            # indicate conversion is complete
                            busy.eq(0),
                            # disable the converter
                            converter_ena.eq(0),
                            # output result
                            bcd.eq(bcd_reg),
                            # return to idle state
                            state.eq(0)
                       )
               })
            ).Else(
                ready.eq(1),
                # reset bit counter
                bit_count.eq(0),
                # indicate not available
                busy.eq(1),
                # disable the converter
                converter_ena.eq(0),
                # clear BCD result port
                bcd.eq(0),
                # reset state machine
                state.eq(0)
            )
        ]

