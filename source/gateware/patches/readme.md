## LiteX Liteeth patches

This directory contains patches for LiteX and Liteeth which
supports multiple RMII PHYs with their own clocks as used in
this project (including etherbone support).

Apply patches with:
```
patch -d /path/to/liteeth -p1 < liteeth.patch
patch -d /path/to/litex -p1 < litex.patch
```

Detailed patch descriptions can be found on github:

* [Control clock output](https://github.com/rprinz08/liteeth/commit/968a4f9c0cd247b662db8a8cdd3b092d623f841e)
* [Multiple external clocks](https://github.com/rprinz08/liteeth/commit/816e011c15727b4bfca81ca51265ad179d0a207d)
* [Etherbone support for multiple interfaces](https://github.com/rprinz08/litex/commit/c99c96bc68911fdf0661841f22acbd507d12117e)

