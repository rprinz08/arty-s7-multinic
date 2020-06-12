from migen import *
from litex.soc.interconnect.csr import *
from litedram.frontend.bist import LFSR


PRBS31 = [27, 30]
PRBS23 = [17, 22]
PRBS15 = [13, 14]
PRBS7  = [ 5,  6]


class Random(Module, AutoCSR):

    def __init__(self, PRBS=PRBS31):

        self._random = CSRStatus(32)

        # # #

        self.submodules.lfsr = lfsr = LFSR(31, n_state=31, taps=PRBS)
        self.sync += self._random.status.eq(lfsr.o)

