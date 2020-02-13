#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
apt-get update
apt-get install -y python3 build-essential python-dev libnetfilter-queue-dev python3-pip net-tools tcpdump tmux
pip3 install -r $CURRENT_DIR/requirements.txt
pip3 install --upgrade service_identity
