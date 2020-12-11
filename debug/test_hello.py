#!/usr/bin/env python3

from litex import RemoteClient

wb = RemoteClient(host="localhost", port=1234, csr_csv="../build/csr.csv", debug=True)
wb.open()

# # #

def hello(data):
    wb.regs.hello_input.write(data)
    x = wb.regs.hello_output.read()
    print("return value is (0x{:02x})".format(x))

hello(0xaa)

# # #

wb.close()
