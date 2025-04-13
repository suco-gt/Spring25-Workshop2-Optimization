from mpi4py import MPI
import numpy as np

def coo_spgemm(m, h, n, A, B):
    comm = MPI.COMM_WORLD

    # TODO: Get entire matrix B onto each processor
    fullB = None

    # TODO: Initialize efficient data structures that allows you to
    # quickly access each nonzero element of A and B using the COO
    # representations. 
    matrix_A = None
    matrix_B = None

    """
    TODO: Spgemm Algorithm
        Iterate through each row i with nonzero values in A:
            For each nonzero value a_{ik} in that row a_i...
                For each nonzero value b_{kj} in the row b_k...
                    value = a_{ik} * b_{kj}
                        if c_{ij} is not inserted into c yet,
                            c_{ij} = value
                        else
                            c_{ij} += value
    """
    res = None

    return res


def csr_spgemm(m, h, n, A, B):
    raise NotImplementedError