#include <stdio.h>
#include <generated/csr.h>
#include "system.h"


// defines ticker functions used by picotcp
uint32_t cpu_clock_freq(void)
{
	return config_clock_frequency_read();
}

uint32_t ticks(void)
{
	return ticker_ticks_read();
}

uint32_t ticks_milliseconds(void)
{
	return ticker_ms_read();
}

uint32_t ticks_seconds(void)
{
	return ticks_milliseconds() / 1000;
}

