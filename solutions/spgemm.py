import mpi4py
from mpi4py import MPI
import numpy as np

def coo_spgemm(m, h, n, A, B):
    comm = MPI.COMM_WORLD

    # TODO: Get entire matrix B onto each processor
    fullB = comm.allgather(B)
    fullB = [item for sublist in fullB for item in sublist]

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
    
    matrix_A = dict()
    matrix_B = dict()
    for A_nnz in A:
        if A_nnz[0] in matrix_A:
            matrix_A[A_nnz[0]].append((A_nnz[1], A_nnz[2]))
        else:
            matrix_A[A_nnz[0]] = [(A_nnz[1], A_nnz[2])]
    for B_nnz in fullB:
        if B_nnz[0] in matrix_B:
            matrix_B[B_nnz[0]].append((B_nnz[1], B_nnz[2]))
        else:
            matrix_B[B_nnz[0]] = [(B_nnz[1], B_nnz[2])]

    matrix_C = dict()
    for keyA, valA in sorted(matrix_A.items()):
        C_key = keyA
        for (k, wA) in valA:
            for (j, wB) in matrix_B[k]:
                val = wA * wB
                if C_key not in matrix_C:
                    matrix_C[C_key] = [(j, val)]
                else:
                    find_cij = False
                    for idx, (cij_j, cij_val) in enumerate(matrix_C[C_key]):
                        if cij_j == j:
                            matrix_C[C_key][idx] = (j, cij_val + val)
                            find_cij = True
                    if not find_cij:
                        matrix_C[C_key].append((j, val))
    
    res = []
    for keyC, valC in sorted(matrix_C.items()):
        valC.sort(key=lambda tup: tup[0])
        for v in valC:
            res.append([keyC, v[0], v[1]])
    return res


def csr_spgemm(m, h, n, A, B):
    raise NotImplementedError