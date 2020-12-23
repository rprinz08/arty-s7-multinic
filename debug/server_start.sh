#!/bin/bash

S=`basename $0`
P=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
PIDF="/var/run/litex_server.pid"
LOGF="/var/log/litex_server.log"
TARGET_IP="10.0.0.42"
TARGET_PORT=4711

if [ -f $PIDF ]; then
	echo "LiteX Server already running. Pidfile (${PIDF}) found."
    exit 1
fi

if (( $EUID != 0 )); then
    if whereis sudo &>/dev/null; then
        sudo -H $0 $*
        exit
    else
        echo "'sudo' utility not found."
        echo "You will need to run this script as root."
        exit
    fi
fi

DEBUG=--debug
if [ "$1x" == "fgx" ]; then
	litex_server \
		$DEBUG \
		--udp --udp-ip=$TARGET_IP --udp-port=$TARGET_PORT
else
	litex_server \
		$DEBUG \
		--udp --udp-ip=$TARGET_IP --udp-port=$TARGET_PORT \
		>$LOGF 2>&1 </dev/null &
	echo $! > $PIDF
fi
