#!/bin/bash

if [ $# -eq 0 ]; then
    salloc --nodes=1 --ntasks-per-node=4 --time=01:00:00
else
    salloc --nodes=1 --ntasks-per-node="$1" --time=01:00:00
fi