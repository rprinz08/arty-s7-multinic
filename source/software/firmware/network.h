#ifndef __NETWORK_H
#define __NETWORK_H

#include "pico_stack.h"
#include "pico_socket.h"
#include "pico_ipv4.h"
#include "pico_icmp4.h"

void net_init(void);
void net_service(void);
void ping_cb(struct pico_icmp4_stats *s);
int ping(void);

#endif

