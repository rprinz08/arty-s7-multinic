-include ../../config.mk
-include ../../tools/kconfig/.config

OS:=$(shell uname)
CC:=$(CROSS_COMPILE)gcc
LD:=$(CROSS_COMPILE)ld
AR:=$(CROSS_COMPILE)ar
RANLIB:=$(CROSS_COMPILE)ranlib
SIZE:=$(CROSS_COMPILE)size
STRIP_BIN:=$(CROSS_COMPILE)strip

CFLAGS+=-DARCH='"$(ARCH)"' -MD -Wall -c -Itest/support
LDFLAGS=
ARFLAGS=rcs

SRCPATH=src
PREFIX=build
BINPATH=$(PREFIX)/lib
INCPATH=$(PREFIX)/include

SOURCES=\
		umm_info.c \
		umm_integrity.c \
		umm_malloc.c \
		umm_poison.c \

OBJECTS=$(SOURCES:%.c=$(BINPATH)/%.o)
DEP=$(OBJECTS:.o=.d)
-include $(DEP)
LIBRARY=$(BINPATH)/libumm.a

all: prepare $(LIBRARY)

$(LIBRARY): $(OBJECTS)
	@mkdir -p $(INCPATH)
	@cp -f $(SRCPATH)/*.h $(INCPATH)
	$(AR) $(ARFLAGS) $@ $(OBJECTS)

$(BINPATH)/%.o: $(SRCPATH)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

prepare:
	-@mkdir -p $(BINPATH)

clean:
	-@rm -rf $(BINPATH)

.PHONY: all clean prepare

