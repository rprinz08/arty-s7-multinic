BUILD_PATH=./build
GATEWARE_BUILD_PATH=$(BUILD_PATH)/gateware
SOFTWARE_BUILD_PATH=$(BUILD_PATH)/software

SOURCE_PATH=./source
GATEWARE_SOURCE_PATH=$(SOURCE_PATH)/gateware
SOFTWARE_SOURCE_PATH=$(SOURCE_PATH)/software

BITSTREAM=$(GATEWARE_BUILD_PATH)/top.bin
FIRMWARE_PATH=$(SOFTWARE_SOURCE_PATH)/firmware
FIRMWARE=$(FIRMWARE_PATH)/firmware.bin
FIRMWARE_FBI=$(FIRMWARE_PATH)/firmware.fbi

IDENTIFIER="Arty-S7 RISC64 v1.0"
IDENTIFIER_VER=true
CSR_JSON=$(BUILD_PATH)/csr.json
DEV = "/dev/ttyUSB0"
UART_BAUD=115200
CPU_TYPE="vexriscv"
CPU_VARIANT="linux"

$(BITSTREAM): $(GATEWARE_SOURCE_PATH)/*.py
	@./make.py build \
		--cpu-type $(CPU_TYPE) \
		--cpu-variant $(CPU_VARIANT) \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH) \
		--ident $(IDENTIFIER) \
		--ident-version $(IDENTIFIER_VER) \
		--uart-baudrate $(UART_BAUD) \
		--csr-json $(CSR_JSON)

build-sw:
	@./make.py build-sw \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH) \
		--ident $(IDENTIFIER) \
		--ident-version $(IDENTIFIER_VER) \
		--csr-json $(CSR_JSON)

build-fpga:
	@./make.py build-sw \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH) \
		--ident $(IDENTIFIER) \
		--ident-version $(IDENTIFIER_VER) \
		--csr-json $(CSR_JSON)

conv:
	@./make.py conv \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH) \
		--ident $(IDENTIFIER) \
		--ident-version $(IDENTIFIER_VER) \
		--csr-json $(CSR_JSON)

load: $(BITSTREAM)
	@./make.py load \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH)

reload:
	@# Does not check for changes in source files. Just uses existing
	@# bitstream.
	@./make.py load \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH)

flash: $(BITSTREAM)
	@./make.py flash \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH)

reflash:
	@# Does not check for changes in source files. Just uses existing
	@# bitstream.
	@./make.py flash \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_BUILD_PATH) \
		--software-dir $(SOFTWARE_BUILD_PATH)

flash-sw:
	@./make.py flash-sw \
		--firmware=$(FIRMWARE_FBI)

term:
	@litex_term --speed $(UART_BAUD) $(DEV)

load-sw:
	@litex_term --kernel $(FIRMWARE) --speed $(UART_BAUD) $(DEV)

SD_CARD = "/media/$(USER)/LITEX"
SD_DEV = $(shell findmnt -n -o SOURCE --target /media/$(USER)/LITEX)
sdcard-init:
ifeq ($(SD_DEV),)
	@echo "SD-Card 'LiteX' not found !!!"
else
	@echo "Initialize LiteX boot SD-Card on $(SD_DEV)"
	-@umount $(SD_DEV)
	@sudo mkfs.fat -n LITEX -F 16 $(SD_DEV)
endif

sdcard:
	@echo "Copy firmware to SD-Card ($(SD_CARD))"
	@if [ -d $(SD_CARD) ]; then \
		cp $(FIRMWARE) /media/$(USER)/LITEX/BOOT.BIN; \
	else \
		echo "SD-Card ($(SD_CARD)) not found !!!"; \
	fi

clean:
	rm -rf build/*
	rm -f vivado.log
	rm -f vivado.jou
	rm -frd .Xil

.PHONY: clean load load-sw reload flash flash-sw reflash conv term sdcard-init sdcard

