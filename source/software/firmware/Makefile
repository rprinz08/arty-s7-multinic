include ../../../build/software/include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

ARCH=$(shell echo $(CPU) | tr a-z A-Z)
$(info ${ARCH})

BUILD_DIRECTORY = $(BUILDINC_DIRECTORY)/..
FIRMWARE_DIRECTORY=$(BUILD_DIRECTORY)/../../source/software/firmware

CRT0 = $(BUILD_DIRECTORY)/libbase/crt0.o
LINKER_LD = linker.ld

OBJECTS = \
	boot-helper.o \
	main.o \
	isr.o \
	uptime.o \
	system.o \
	stdio_wrap.o \
	reboot.o \
	ci.o \
	tools.o \
	network.o \
	network_if.o

CFLAGS += \
	$(CPUFLAGS) \
	-I$(BUILDINC_DIRECTORY) \
	-I$(FIRMWARE_DIRECTORY) \
	-I../third_party/umm_malloc/umm_malloc/build/include \
	-I../third_party/picotcp/picotcp/build/include

CFLAGS += \
	-Wall \
	-Werror \
	-Wno-error=unused-function \
	-Wno-error=unused-variable

CFLAGS += \
	-DARCH=$(CPU) \
	-D$(ARCH)

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
		-L$(BUILD_DIRECTORY)/libcompiler_rt -lcompiler_rt \
		-L../third_party/umm_malloc/umm_malloc/build/lib -lumm \
		-L../third_party/picotcp/picotcp/build/lib -lpicotcp
	chmod -x $@

firmware.elf: $(FIRMWARE_DIRECTORY)/$(LINKER_LD) $(OBJECTS)

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

boot-helper.o: $(CPU_DIRECTORY)/boot-helper.S
	$(assemble)

%.o: $(FIRMWARE_DIRECTORY)/%.c
	$(compile)

%.o: $(FIRMWARE_DIRECTORY)/%.S
	$(assemble)

term:
	@litex_term.py --speed 115200 /dev/ttyUSB1

load: firmware.bin
	@litex_term.py --speed 115200 --kernel ./firmware.bin /dev/ttyUSB1

clean:
	$(RM) $(OBJECTS) $(OBJECTS:.o=.d) firmware.fbi firmware.elf firmware.bin .*~ *~

.PHONY: all clean term load

