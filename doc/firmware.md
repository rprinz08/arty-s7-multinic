# Demo Firmware

The included demo firmware is used to try out concepts and to
show sample code.

* Included is a sample on how to use [Configuration Status Registers (CSR)](https://github.com/enjoy-digital/litex/wiki/CSR-Bus) to talk to the FPGA from firmware. The `echo` sample sends a byte to the FPGA gateware where it is XOR'ed with 0xff and the result returned to the firmware which is then displayed on the serial console.

* The `time` sample shows the free running CPU clock cycle ticker and
derived millisecond subticker in FPGA. The later is used by the 
network stack described below.

* `uptime` shows the time elapsed since boot

* A simple [Pseudo Random Number Generator PRNG](https://en.wikipedia.org/wiki/Pseudorandom_number_generator) is included in the gateware. 
It is based on a [Linear Feedback Shift Register (LFSR)](https://en.wikipedia.org/wiki/Linear-feedback_shift_register) configured as [Pseudo Random Binary Sequence (PRBS31)](https://en.wikipedia.org/wiki/Pseudorandom_binary_sequence). Its output can be shown with `random [runs]` and an optional value how many numbers to display (default 500).

* The firmware includes the [umm_malloc Memory Manager](https://github.com/rhempel/umm_malloc) which enables dynamic memory allocations ([malloc, free](https://man7.org/linux/man-pages/man3/malloc.3.html)). The `malloc [runs]` command performs a simple test allocating an amount of memory, fill it with data, read it back, and compare the results. An optional value specifies how often this test should be performed (default 500).

* [PicoTCP](https://github.com/tass-belgium/picotcp) is a very lightwight network stack which is included in the firmware. The demo `ping` command pings (IP4, ICMP) a target host. It uses the first network interface. Configuration (Ethernet MAC address, IP4 address, netmask, ping target IP4 address and number of pings) can be found in `config.h`. The files `network.c` and `network_if.c` show how to initialize and use PicoTCP and how a device driver for LiteX Liteeth looks.

The following log shows a sample run of the firmware:
```
VEXRISCV
[LXTERM] Starting....

        __   _ __      _  __
       / /  (_) /____ | |/_/
      / /__/ / __/ -_)>  <
     /____/_/\__/\__/_/|_|
   Build your hardware, easily!

 (c) Copyright 2012-2020 Enjoy-Digital
 (c) Copyright 2007-2015 M-Labs

 BIOS built on Jun 17 2020 17:05:47
 BIOS CRC passed (707679a9)

 Migen git sha1: b1b2b29
 LiteX git sha1: efbe1690

--=============== SoC ==================--
CPU:       VexRiscv @ 100MHz
BUS:       WISHBONE 32-bit - 4GiB
CSR:       8-bit data
ROM:       32KiB
SRAM:      4KiB
L2:        8KiB
MAIN-RAM:  262144KiB

--========== Initialization ============--
Ethernet init...
Initializing SDRAM...
SDRAM now under software control
SDRAM now under software control
Read leveling:
m0, b00: |00000000000000000000000000000000| delays: -
m0, b01: |00000000000000000000000000000000| delays: -
m0, b02: |00000000000000000000000000000000| delays: -
m0, b03: |00000000000000000000000000000000| delays: -
m0, b04: |00000000000000000000000000000000| delays: -
m0, b05: |00000000000000000000000000000000| delays: -
m0, b06: |00000000000000000000000000000000| delays: -
m0, b07: |00000000000000000000000000000000| delays: -
m0, b08: |00000000000000000000000000000000| delays: -
m0, b09: |00000000000000000000000000000000| delays: -
m0, b10: |00000000000000000000000000000000| delays: - 
m0, b11: |00000000000000000000000000000000| delays: -
m0, b12: |00000000000000000000000000000000| delays: -
m0, b13: |11000000000000000000000000000000| delays: 00+-00
m0, b14: |00001111111111111100000000000000| delays: 11+-07
m0, b15: |00000000000000000000111111111111| delays: 26+-06
best: m0, b14 delays: 11+-07
m1, b00: |00000000000000000000000000000000| delays: -
m1, b01: |00000000000000000000000000000000| delays: -
m1, b02: |00000000000000000000000000000000| delays: -
m1, b03: |00000000000000000000000000000000| delays: -
m1, b04: |00000000000000000000000000000000| delays: -
m1, b05: |00000000000000000000000000000000| delays: -
m1, b06: |00000000000000000000000000000000| delays: -
m1, b07: |00000000000000000000000000000000| delays: -
m1, b08: |00000000000000000000000000000000| delays: -
m1, b09: |00000000000000000000000000000000| delays: -
m1, b10: |00000000000000000000000000000000| delays: -
m1, b11: |00000000000000000000000000000000| delays: -
m1, b12: |00000000000000000000000000000000| delays: -
m1, b13: |00000000000000000000000000000000| delays: 00+-00
m1, b14: |00000111111111111100000000000000| delays: 11+-06
m1, b15: |00000000000000000000111111111111| delays: 26+-06
best: m1, b14 delays: 11+-06
SDRAM now under hardware control
Memtest OK
Memspeed Writes: 229Mbps Reads: 327Mbps

--============== Boot ==================--
Booting from serial...
Press Q or ESC to abort boot completely.
sL5DdSMmkekro
[LXTERM] Received firmware download request from the device.
[LXTERM] Uploading ./firmware.bin to 0x40000000 (288804 bytes)...
[LXTERM] Upload complete (3.7KB/s).
[LXTERM] Booting the device.
[LXTERM] Done.
Executing booted program at 0x40000000

--============= Liftoff! ===============--
net_init: Start ...
eth_init: ...
Network interfaces: (3)
eth_init: Done
pTCP: Init
Protocol ethernet registered (layer: 2).
Protocol ipv4 registered (layer: 3).
Protocol ipv6 registered (layer: 3).
Protocol icmp4 registered (layer: 4).
Protocol icmp6 registered (layer: 4).
Protocol igmp registered (layer: 4).
Protocol udp registered (layer: 4).
Protocol tcp registered (layer: 4).
pTCP: Create device (eth0)
pTCP: MAC address (00:01:bb:08:15:00)
pTCP: Set device (eth0) IP4 address to (10.0.0.50)
pTCP: Set device (eth0) IP4 netmask to (255.255.255.0)
pTCP: Add device (eth0) to stack
Assigned ipv4 10.0.0.50 to device eth0
net_init: Done
Hello firmware booting...

HELLO >
IPv6: DAD verified valid address.

HELLO >help

Available commands:
hello value      - Returns value xor'ed with 0xff in FPGA
time             - show current clock ticks
uptime           - show system uptime in seconds
random [runs]    - show random number generator values, default [500] runs
malloc [runs]    - test UMM malloc, default [500] runs
ping             - ping host (10.0.0.100) via network interface (eth0)
reboot           - reboot CPU
help             - this command

HELLO >ping

Ping: Start ...
pTCP: Ping (10.0.0.100) for (10) times
64 bytes from 10.0.0.100: icmp_req=1 ttl=64 time=4 ms
64 bytes from 10.0.0.100: icmp_req=2 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=3 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=4 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=5 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=6 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=7 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=8 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=9 ttl=64 time=2 ms
64 bytes from 10.0.0.100: icmp_req=10 ttl=64 time=2 ms

Ping: Done

HELLO >

```
