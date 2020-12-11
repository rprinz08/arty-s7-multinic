## LiteX Liteeth patches

This directory contains patches for LiteX and Liteeth which
supports multiple RMII PHYs with their own clocks as used in
this project (including etherbone support).

Apply patches with:
```
patch -d /path/to/liteeth -p1 < liteeth.patch
patch -d /path/to/litex -p1 < litex.patch
```

Detailed patch description can be found on github:

* [Reset patch](https://github.com/rprinz08/liteeth/commit/6ac06a8423d326f111316909a07afba65db71fe0)
* [Multy RMII PHY patch](https://github.com/rprinz08/liteeth/commit/ed355c5aae09e2234098910da4ee220956210371)
* [Control clock output](https://github.com/rprinz08/liteeth/commit/66660f6931ec5b08ce531ed030829e0ba198311a)

