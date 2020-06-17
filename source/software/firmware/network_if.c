#include <stdio.h>
#include <time.h>
#include <generated/soc.h>
#include <generated/csr.h>
#include <generated/mem.h>

#include "umm_malloc.h"

#include "tools.h"
#include "stdio_wrap.h"
#include "network_if.h"


static unsigned int rxslot;
static unsigned int rxlen;
static ethernet_buffer *rxbuffer;

static unsigned int txslot;
static unsigned int txlen;
static ethernet_buffer *txbuffer;

static int send(struct pico_device *dev, void *buf, int len);
static int receive_poll(struct pico_device *dev, int loop_score);


void eth_init(void)
{
    printf("eth_init: ...\n");

    uint8_t iface_count = 0;
#ifdef CSR_ETHMAC_BASE
    iface_count++;
#endif
#ifdef CSR_ETHMAC1_BASE
    iface_count++;
#endif
#ifdef CSR_ETHMAC2_BASE
    iface_count++;
#endif
#ifdef CSR_ETHMAC3_BASE
    iface_count++;
#endif
    printf("Network interfaces: (%d)\n", iface_count);

    // TODO: create dynamic structure of all network interfaces here

    printf("eth_init: Done\n");
}


struct pico_device *pico_eth_create(const char *name, const uint8_t *mac)
{
    printf("pTCP: Create device (%s)\n",
            name);
    printf("pTCP: MAC address (%s)\n", mac_addr_fmt(mac));

    // create picoTCP device structure
    struct pico_device* eth_dev = PICO_ZALLOC(sizeof(struct pico_device));
    if(!eth_dev) {
        return NULL;
    }

    // ------------------------------------------------------------------------
    // init hw
#ifdef CSR_ETHPHY_CRG_RESET_ADDR
    ethphy_crg_reset_write(1);
    busy_wait(200);
    ethphy_crg_reset_write(0);
    busy_wait(200);
#endif

    ethmac_sram_reader_ev_pending_write(ETHMAC_EV_SRAM_READER);
    ethmac_sram_writer_ev_pending_write(ETHMAC_EV_SRAM_WRITER);

    txslot = 0;
    ethmac_sram_reader_slot_write(txslot);
    txbuffer = (ethernet_buffer *)(ETHMAC_BASE + ETHMAC_SLOT_SIZE * (ETHMAC_RX_SLOTS + txslot));

    rxslot = 0;
    rxbuffer = (ethernet_buffer *)(ETHMAC_BASE + ETHMAC_SLOT_SIZE * rxslot);
    // ------------------------------------------------------------------------

    // set picoTCP tx/rx callbacks
    eth_dev->send = send;
    eth_dev->poll = receive_poll;

    // init new device
    if(pico_device_init(eth_dev, name, mac) != 0) {
        dbg("Device init failed.\n");
        PICO_FREE(eth_dev);
        return NULL;
    }

    return eth_dev;
}


static int send(struct pico_device *dev, void *buf, int len)
{
    while(!(ethmac_sram_reader_ready_read()));

    txlen = len;
    if(txlen > ETHMAC_SLOT_SIZE) {
        printf("TX packet len (%d) > ethernet MAC slot size (%d) - truncated",
            txlen, ETHMAC_SLOT_SIZE);
        txlen = ETHMAC_SLOT_SIZE;
    }
    memcpy(txbuffer->raw, buf, txlen);

    ethmac_sram_reader_slot_write(txslot);
    ethmac_sram_reader_length_write(txlen);
    ethmac_sram_reader_start_write(1);

    txslot = (txslot + 1) % ETHMAC_TX_SLOTS;
    txbuffer = (ethernet_buffer *)(ETHMAC_BASE + ETHMAC_SLOT_SIZE * \
            (ETHMAC_RX_SLOTS + txslot));

    //printf("\n** TX (%d) **\n", txlen);
    //dump_hex(buf, txlen);
    //printf("\n");

    return txlen;
}


static int receive_poll(struct pico_device *dev, int loop_score)
{
    while(loop_score > 0) {

        if(!(ethmac_sram_writer_ev_pending_read() & ETHMAC_EV_SRAM_WRITER))
            break;

        rxslot = ethmac_sram_writer_slot_read();
        rxbuffer = (ethernet_buffer *)(ETHMAC_BASE + ETHMAC_SLOT_SIZE * rxslot);
        rxlen = ethmac_sram_writer_length_read();

        pico_stack_recv(dev, &rxbuffer->raw[0], rxlen);

        ethmac_sram_writer_ev_pending_write(ETHMAC_EV_SRAM_WRITER);

        //printf("\n** RX (%d) **\n", rxlen);
        //dump_hex(buf, txlen);
        //printf("\n");

        loop_score--;
    }

    return loop_score;
}

