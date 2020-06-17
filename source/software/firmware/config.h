#ifndef __CONFIG_H
#define __CONFIG_H

// The following defines configure network interfaces
#define ETH0_NAME               "eth0"
#define ETH0_MAC                "00:01:bb:08:15:00"
#define ETH0_IP4_ADDR           "10.0.0.50"
#define ETH0_IP4_MASK           "255.255.255.0"

#define ETH0_IP4_PING_ADDR      "10.0.0.100"
#define ETH0_IP4_PING_COUNT     10

// TODO: also for remaining network interfaces
// TODO: CLI commands to modify config
// TODO: read config from SD-Card

#endif

