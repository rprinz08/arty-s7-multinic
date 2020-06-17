#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <time.h>
#include <console.h>
#include <generated/csr.h>
#include <generated/mem.h>

#include "stdio_wrap.h"
#include "system.h"
#include "network.h"
#include "ci.h"
#include "uptime.h"

int main(void)
{
    irq_setmask(0);
    irq_setie(1);
    uart_init();
    time_init();
    umm_init();
#ifdef CSR_ETHMAC_BASE
    net_init();
#endif

    wputs("Hello firmware booting...\n");

    ci_prompt();
    while(1) {
        uptime_service();
        ci_service();
        net_service();
    }

    return 0;
}

