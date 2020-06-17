#include <stdio.h>
#include <string.h>
#include <generated/csr.h>

#include "umm_malloc.h"
#include "tools.h"


uint8_t hex_to_int(const char c)
{
    if(c >= 'a' && c <= 'f')
        return c - 'a' + 10;

    if(c >= 'A' && c <= 'F')
        return c - 'A' + 10;

    if(c >= '0' && c <= '9')
        return c - '0';

    return 0;
}


int strcasecmp (const char *s1, const char *s2)
{
    const unsigned char *p1 = (const unsigned char *) s1;
    const unsigned char *p2 = (const unsigned char *) s2;
    int result;

    if (p1 == p2)
        return 0;

    while ((result = tolower(*p1) - tolower(*p2++)) == 0)
        if (*p1++ == '\0')
            break;

    return result;
}


uint8_t *mac_addr_parse(const char *mac_str) {
    uint8_t *bytes = umm_malloc(6);
    if(bytes == NULL)
        return NULL;

    int i, j;
    for(i=0; i<6; i++) {
        bytes[i] = 0;

        j = 0;
        while( ((*mac_str) != '\0') && ((*mac_str) != ':') ) {
            if(j > 1) {
                umm_free(bytes);
                return NULL;
            }
            //printf("%d: (%c) == (%d)\n", i, *mac_str, bytes[i]);
            bytes[i] <<= 4;
            bytes[i] |= hex_to_int(*mac_str);
            mac_str++;
            j++;
        }
        if(*mac_str == ':')
            mac_str++;
    }

    if( (i != 6) || (*mac_str != '\0')) {
        umm_free(bytes);
        return NULL;
    }

    return bytes;
}


char *mac_addr_fmt_r(const uint8_t *mac, char *buf, size_t len)
{
    if(mac == NULL || buf == NULL || len < 18)
        return NULL;

    snprintf(buf, len, "%02x:%02x:%02x:%02x:%02x:%02x",
        mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    return buf;
}


char *mac_addr_fmt(const uint8_t *mac)
{
    static char buf[18];

    if(mac == NULL)
        return "";

    snprintf(buf, sizeof(buf), "%02x:%02x:%02x:%02x:%02x:%02x",
        mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    return buf;
}


void dump_hex(const void* data, const size_t size) {
    char ascii[17];
    size_t i, j;
    ascii[16] = '\0';

    for(i=0; i<size; ++i) {
        printf("%02X ", ((unsigned char*)data)[i]);

        if(((unsigned char*)data)[i] >= ' ' && ((unsigned char*)data)[i] <= '~')
            ascii[i % 16] = ((unsigned char*)data)[i];
        else
            ascii[i % 16] = '.';

        if((i+1) % 8 == 0 || i+1 == size) {
            printf(" ");

            if((i+1) % 16 == 0)
                printf("|  %s \n", ascii);
            else
                if (i+1 == size) {
                    ascii[(i+1) % 16] = '\0';

                    if((i+1) % 16 <= 8)
                        printf(" ");

                    for(j = (i+1) % 16; j < 16; ++j)
                        printf("   ");

                    printf("|  %s \n", ascii);
                }
        }
    }
}

