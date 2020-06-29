#ifndef __UPTIME_H
#define __UPTIME_H

#ifdef CSR_TIMER0_UPTIME_CYCLES_ADDR
const char* uptime_str(unsigned long);
void uptime(void);
#endif

#endif

