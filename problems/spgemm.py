import mpi4py
from mpi4py import MPI
import numpy as np

def coo_spgemm(m, h, n, A, B):
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    # Get entire matrix B onto each processor
    fullB = comm.allgather(B)

    """
    Iterate through each row i with nonzero values in A:
        For each nonzero value a_{ik} in that row a_i...
            For each nonzero value b_{kj} in the row b_k...
                value = a_{ik} * b_{kj}
                    if c_{ij} is not inserted into c yet,
                        c_{ij} = value
                    else
                        c_{ij} += value
    """

    matrix_A = dict()
    matrix_B = dict()
    for A_nnz in A:
        matrix_A[A_nnz[0]].append((A_nnz[1], A_nnz[2]))
    for B_nnz in B:
        matrix_B[B_nnz[0]].append((B_nnz[1], B_nnz[2]))

    matrix_C = dict()
    
    return []


def csr_spgemm(m, h, n, A, B):
    return []