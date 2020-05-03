#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>
#include <generated/mem.h>

#include "reboot.h"

#include "ci.h"

static char *readstr(void)
{
	char c[2];
	static char s[64];
	static int ptr = 0;

	if(readchar_nonblock()) {
		c[0] = readchar();
		c[1] = 0;
		switch(c[0]) {
			case 0x7f:
			case 0x08:
				if(ptr > 0) {
					ptr--;
					putsnonl("\x08 \x08");
				}
				break;
			case 0x07:
				break;
			case '\r':
			case '\n':
				s[ptr] = 0x00;
				putsnonl("\n");
				ptr = 0;
				return s;
			default:
				if(ptr >= (sizeof(s) - 1))
					break;
				putsnonl(c);
				s[ptr] = c[0];
				ptr++;
				break;
		}
	}

	return NULL;
}

static char *get_token(char **str)
{
	char *c, *d;

	c = (char *)strchr(*str, ' ');
	if(c == NULL) {
		d = *str;
		*str = *str+strlen(*str);
		return d;
	}
	*c = 0;
	d = *str;
	*str = c+1;
	return d;
}

static int get_number(const char *str) {
	return atoi(str);
}

static void help(void)
{
	puts("display value  - Display 8bit values on 7Segment display on PMOD-D");
	puts("hello value    - Returns value xor'ed with 0xff in FPGA");
	//puts("gpio value     - Send 8bit values to PMOD-C");
	puts("reboot         - reboot CPU");
	puts("help           - this command");
}

void ci_prompt(void)
{
	printf("HELLO>");
}

void ci_service(void)
{
	char *str;
	char *token;

	str = readstr();
	if(str == NULL) return;

	token = get_token(&str);

	if(strcmp(token, "help") == 0) {
		puts("Available commands:");
		help();
	}
	else
	if(strcmp(token, "reboot") == 0) {
		reboot();
	}
	else
	// The 'hello' test command sends 8bit value to the input CSR of the
	// FPGA co-designed sample XOR module. Then reads back the value
	// XORed (in FPGA) with 0xff and displays the result
	if(strcmp(token, "hello") == 0) {
		char *val_raw = get_token(&str);
		int val = get_number(val_raw);
		if(val < 0 || val > 255) {
			printf("Only numeric input between 0 and 255!\n");
		}
		else {
			hello_input_write(val);
			uint8_t result = hello_output_read();
			printf("Write (%02x), Read (%02x)\n", val, result);
		}
	}
	else
	// GPIO test
	/*
	if(strcmp(token, "gpio") == 0) {
		char *val_raw = get_token(&str);
		int val = get_number(val_raw);
		if(val < 0 || val > 255) {
			printf("Only numeric input between 0 and 255!\n");
		}
		else {
			pmodd_out_write((uint8_t)val);
		}
	}
	else
	*/
	// Seven Segment display test
	if(strcmp(token, "display") == 0) {
		char *val_raw = get_token(&str);
		int val = get_number(val_raw);
		if(val < 0 || val > 255) {
			printf("Only numeric input between 0 and 255!\n");
		}
		else {
			disp7_dispval_write((uint8_t)val);
		}
	}

	ci_prompt();
}

