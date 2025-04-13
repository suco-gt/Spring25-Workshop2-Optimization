#!/bin/bash

if [ "$1" == "test" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python hello_world.py
fi

if [ "$1" == "brute" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input.txt -o brute
fi

if [ "$1" == "spgemm" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input.txt -o spgemm1
fi