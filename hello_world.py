import mpi4py
from mpi4py import MPI
import numpy as np
import os


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
print("Numpy and MPI4Py installed successfully!")
print(f"Numpy Version: {np.__version__}")
print(f"MPI4Py Version: {mpi4py.__version__}")
print(f"Hello world from processor {rank}!\n")
