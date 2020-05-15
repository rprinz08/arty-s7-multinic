from litex.soc.interconnect.csr import *

# A simple FPGA "hello world" addition to a LiteX SOC design
# as described in https://debugmo.de/2014/09/ov3-fpga-helloworld/
# Implements a co-design for a hardware XOR module in FPGA. Creates
# an input and an output register which returns the input XORed with
# 0xff.
class Hello(Module, AutoCSR):
    def __init__(self):
      self._input = CSRStorage(8)
      self._output = CSRStatus(8)

      self.sync += self._output.status.eq(self._input.storage ^ 0xff)

