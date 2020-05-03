include ../../build/software/include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

BUILD_DIRECTORY = $(BUILDINC_DIRECTORY)/..
FIRMWARE_DIRECTORY=$(BUILD_DIRECTORY)/../../source/firmware

ifeq ($(COPY_TO_MAIN_RAM), 1)
CRT0 = $(BUILD_DIRECTORY)/libbase/crt0-$(CPU)-ctr.o
LINKER_LD = linker-ctr.ld
else
CRT0 = $(BUILD_DIRECTORY)/libbase/crt0-$(CPU)-xip.o
LINKER_LD = linker-xip.ld
endif

OBJECTS = \
	boot-helper-$(CPU).o \
	main.o \
	isr.o \
	uptime.o \
	stdio_wrap.o \
	reboot.o \
	ci.o

CFLAGS += \
	$(CPUFLAGS) \
	-I$(BUILDINC_DIRECTORY) \
	-I$(FIRMWARE_DIRECTORY)

CFLAGS += \
	-Wall \
	-Werror \
	-Wno-error=unused-function \
	-Wno-error=unused-variable

LDFLAGS += \

all: firmware.bin firmware.fbi

%.fbi: %.bin
ifeq ($(CPUENDIANNESS), little)
	$(PYTHON) -m litex.soc.software.mkmscimg -f --little $< -o $@
else
	$(PYTHON) -m litex.soc.software.mkmscimg -f $< -o $@
endif

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@

firmware.elf: $(CRT0) $(BUILD_DIRECTORY)/libbase/libbase-nofloat.a $(BUILD_DIRECTORY)/libcompiler_rt/libcompiler_rt.a
	$(LD) $(LDFLAGS) \
		-T $(FIRMWARE_DIRECTORY)/$(LINKER_LD) \
		-N -o $@ \
		$(CRT0) \
        $(OBJECTS) \
        -L$(BUILD_DIRECTORY)/libbase -lbase-nofloat \
        -L$(BUILD_DIRECTORY)/libcompiler_rt -lcompiler_rt
	chmod -x $@

firmware.elf: $(FIRMWARE_DIRECTORY)/$(LINKER_LD) $(OBJECTS)

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

boot-helper-$(CPU).S: $(BIOS_DIRECTORY)/boot-helper-$(CPU).S
	cp $< $@

boot-helper-$(CPU).o: boot-helper-$(CPU).S
	$(assemble)

%.o: $(FIRMWARE_DIRECTORY)/%.c
	$(compile)

%.o: $(FIRMWARE_DIRECTORY)/%.S
	$(assemble)

load: firmware.bin
	@litex_term.py --speed 9600 --kernel ./firmware.bin /dev/ttyUSB2

clean:
	$(RM) $(OBJECTS) $(OBJECTS:.o=.d) firmware.fbi firmware.elf firmware.bin .*~ *~

.PHONY: all clean load

