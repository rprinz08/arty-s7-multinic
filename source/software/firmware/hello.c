#include <stdlib.h>
#include <stdio.h>

#include <stdbool.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <time.h>
#include <generated/csr.h>
#include <generated/mem.h>
#include <hw/flags.h>
#include <console.h>
#include <system.h>

int main(void) {
    irq_setmask(0);
    irq_setie(1);
    uart_init();

    wprintf("Hello firmware booting...\n");

    return(42);
}

