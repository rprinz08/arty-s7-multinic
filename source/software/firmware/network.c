#include <stdio.h>
#include <string.h>
#include <time.h>
#include <generated/csr.h>
#include <time.h>

#include "stdio_wrap.h"
#include "config.h"
#include "tools.h"
#include "network_if.h"
#include "network.h"


struct pico_device *eth0;


void net_init(void)
{
    printf("net_init: Start ...\n");
    eth_init();

    // initialize picoTCP stack
    printf("pTCP: Init\n");
    pico_stack_init();

    // create and configure network interface
    const char *dev_name = ETH0_NAME;
    const char *dev_ip4_addr_str = ETH0_IP4_ADDR;
    struct pico_ip4 dev_ip4_addr;
    const char *dev_ip4_mask_str = ETH0_IP4_MASK;
    struct pico_ip4 dev_ip4_mask;
    const char *mac_str = ETH0_MAC;
    const uint8_t *mac = mac_addr_parse(mac_str);
    if(mac == NULL) {
        printf("Error: Parsing device (%s) MAC address (%s)\n",
                dev_name, mac_str);
        return;
    }

    eth0 = pico_eth_create(dev_name, mac);
    if(eth0 == NULL) {
        printf("Error: Creating network device (%s)\n",
                dev_name);
        return;
    }

    printf("pTCP: Set device (%s) IP4 address to (%s)\n",
            dev_name, dev_ip4_addr_str);
    pico_string_to_ipv4(dev_ip4_addr_str, &dev_ip4_addr.addr);

    printf("pTCP: Set device (%s) IP4 netmask to (%s)\n",
            dev_name, dev_ip4_mask_str);
    pico_string_to_ipv4(dev_ip4_mask_str, &dev_ip4_mask.addr);

    printf("pTCP: Add device (%s) to stack\n",
            dev_name);
    pico_ipv4_link_add(eth0, dev_ip4_addr, dev_ip4_mask);

    printf("net_init: Done\n");
}


void net_service(void)
{
    pico_stack_tick();
}


static int finished = 0;

// gets called when the ping receives a reply, or encounters a problem
void ping_cb(struct pico_icmp4_stats *s)
{
    char host[30];
    pico_ipv4_to_string(host, s->dst.addr);

    if (s->err == 0) {
        printf("%lu bytes from %s: icmp_req=%lu ttl=%lu time=%lu ms\n",
                s->size, host, s->seq, s->ttl, (long unsigned int)s->time);
        if (s->seq >= ETH0_IP4_PING_COUNT)
            finished = 1;
    } else {
        printf("PING %lu to %s: Error %d\n",
                s->seq, host, s->err);
        finished = 1;
    }
}

int ping(void)
{
    const int ping_interval = 1000; // ms
    const int ping_timeout = 10000; // ms
    const int ping_size = 64; // bytes

    printf("Ping: Start ...\n");

    finished = 0;
    char *target_ip4_addr_str = ETH0_IP4_PING_ADDR;

    printf("pTCP: Ping (%s) for (%d) times\n",
            target_ip4_addr_str, ETH0_IP4_PING_COUNT);

    int id = pico_icmp4_ping(target_ip4_addr_str, ETH0_IP4_PING_COUNT,
                            ping_interval, ping_timeout, ping_size,
                            ping_cb);
    if (id == -1)
        return -1;

    while (finished != 1)
    {
        pico_stack_tick();
        PICO_IDLE();
    }
    pico_stack_tick();

    pico_icmp4_ping_abort(id);

    printf("\nPing: Done\n");
    return 0;
}

