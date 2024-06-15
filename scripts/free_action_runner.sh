#!/bin/bash

if [ $(uname) == "Darwin" ]; then
    exit 0
fi

sudo df -h
sudo rm -rf /usr/share/dotnet
sudo rm -rf /opt/ghc
sudo rm -rf "/usr/local/share/boost"
sudo rm -rf "$AGENT_TOOLSDIRECTORY"
sudo rm -rf /usr/local/lib/android
sudo rm -rf /opt/hostedtoolcache
sudo rm -rf /__t/CodeQL
sudo df -h
