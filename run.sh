#!/bin/bash

if [ "$1" == "test" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python hello_world.py
fi

if [ "$1" == "intro" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python solutions/0-mpi-intro.py
fi

if [ "$1" == "brute" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input.txt -o brute
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input1.txt -o brute
fi

if [ "$1" == "spgemm" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input.txt -o spgemm1
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input1.txt -o spgemm1
fi

if [ "$1" == "cannon" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input.txt -o cannon
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input1.txt -o cannon
fi

if [ "$1" == "blocked" ]; then
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input.txt -o blocked
    mpiexec -n "$SLURM_NTASKS_PER_NODE" python main.py -f tests/input1.txt -o blocked
fi