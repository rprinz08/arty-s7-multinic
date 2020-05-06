BUILD_PATH=./build
GATEWARE_PATH=$(BUILD_PATH)/gateware
SOFTWARE_PATH=$(BUILD_PATH)/software
BITSTREAM=$(GATEWARE_PATH)/top.bin
FIRMWARE_PATH=./source/firmware
FIRMWARE=$(FIRMWARE_PATH)/firmware.bin
IDENTIFIER="Arty-S7 RISC64 v1.0"
IDENTIFIER_VER=true
DEV = "/dev/ttyUSB0"
UART_BAUD=115200

$(BITSTREAM): source/*.py
	@./make.py build \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_PATH) \
		--software-dir $(SOFTWARE_PATH) \
		--ident $(IDENTIFIER) \
		--ident-version $(IDENTIFIER_VER) \
		--uart-baudrate $(UART_BAUD)

conv:
	@./make.py conv \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_PATH) \
		--software-dir $(SOFTWARE_PATH) \
		--ident $(IDENTIFIER) \
		--ident-version $(IDENTIFIER_VER)

load: $(BITSTREAM)
	@./make.py load \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_PATH) \
		--software-dir $(SOFTWARE_PATH)

reload:
	@# Does not check for changes in source files. Just uses existing
	@# bitstream.
	@./make.py load \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_PATH) \
		--software-dir $(SOFTWARE_PATH)

flash: $(BITSTREAM)
	@./make.py flash \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_PATH) \
		--software-dir $(SOFTWARE_PATH)

reflash:
	@# Does not check for changes in source files. Just uses existing
	@# bitstream.
	@./make.py flash \
		--output-dir $(BUILD_PATH) \
		--gateware-dir $(GATEWARE_PATH) \
		--software-dir $(SOFTWARE_PATH)

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

.PHONY: clean load reload flash reflash conv term sdcard-init sdcard

