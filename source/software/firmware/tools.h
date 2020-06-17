#ifndef __TOOLS_H
#define __TOOLS_H


#define HINIBBLE(x) ((uint8_t)(((x) & 0xF0) >> 4))
#define LONIBBLE(x) ((uint8_t)((x) & 0x0F))

#define tolower(c) ((unsigned char)(c) - 'A' + 'a')
#define toupper(c) ((unsigned char)(c) - 'a' + 'A')


static __inline unsigned digits(unsigned num, int radix)
{
    unsigned count = 0;

    if(!num)
        return 1;
    do {
        num /= radix;
        count++;
    } while(num);

    return count;
}


static __inline char nibbletochar(uint8_t n, _Bool uppercase)
{
    if(n >= 0x0 && n <= 0x9)
        return '0' + n;
    else
        if(n >= 0xa && n <= 0xf)
            return (uppercase ? 'A' : 'a') + (n - 0xa);
    return -1;
}


uint8_t hex_to_int(const char c);
int strcasecmp (const char *s1, const char *s2);
uint8_t *mac_addr_parse(const char *mac_str);
char *mac_addr_fmt_r(const uint8_t *mac, char *buf, size_t len);
char *mac_addr_fmt(const uint8_t *mac);
void dump_hex(const void* data, const size_t size);

#endif

