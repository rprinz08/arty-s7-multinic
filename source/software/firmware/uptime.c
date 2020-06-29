#include <stdio.h>
#include <string.h>
#include <time.h>

#include <generated/csr.h>

#include "uptime.h"
#include "stdio_wrap.h"


#ifdef CSR_TIMER0_UPTIME_CYCLES_ADDR
const char* uptime_str(unsigned long uptime_seconds)
{
    static char buffer[9];
    sprintf(buffer, "%02lu:%02lu:%02lu",
        (uptime_seconds / 3600) % 24,
        (uptime_seconds / 60) % 60,
        uptime_seconds % 60);
    return buffer;
}

void uptime(void)
{
    unsigned long uptime, uptime_seconds;

    timer0_uptime_latch_write(1);
    uptime = timer0_uptime_cycles_read();
    uptime_seconds = uptime / CONFIG_CLOCK_FREQUENCY;

    printf("Uptime: %lu sys_clk cycles / %lu seconds / %s\n",
        uptime, uptime_seconds, uptime_str(uptime_seconds));
}
#endif

