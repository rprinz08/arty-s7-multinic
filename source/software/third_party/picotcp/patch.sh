#!/bin/bash

#DRY=--dry-run

cd ./picotcp
patch $DRY -p1 -i ../vexriscv.patch

