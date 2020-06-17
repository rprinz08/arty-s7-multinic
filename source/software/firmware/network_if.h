#ifndef __NETWORK_IF_H
#define __NETWORK_IF_H

#include <generated/soc.h>

#include "pico_stack.h"
#include "pico_ipv4.h"
#include "pico_icmp4.h"
#include "pico_device.h"


#define ETHMAC_EV_SRAM_WRITER   0x1
#define ETHMAC_EV_SRAM_READER   0x1

typedef union {
    unsigned char raw[ETHMAC_SLOT_SIZE];
} ethernet_buffer;

/*
extern unsigned int rxslot;
extern unsigned int rxlen;
extern ethernet_buffer *rxbuffer;

extern unsigned int txslot;
extern unsigned int txlen;
extern ethernet_buffer *txbuffer;
*/

void eth_init(void);
struct pico_device *pico_eth_create(const char *name, const uint8_t *mac);
//static int send(struct pico_device *dev, void *buf, int len);
//static int receive_poll(struct pico_device *dev, int loop_score);

#endif

