#ifndef __SYS_H
#define __SYS_H

#include "umm_malloc.h"

uint32_t cpu_clock_freq(void);
uint32_t ticks(void);
uint32_t ticks_milliseconds(void);
uint32_t ticks_seconds(void);

#endif

