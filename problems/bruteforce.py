import numpy as np
import argparse
import time


def bruteforce(m, h, n, A, B):
    """
    Args:
        A: (m x h) matrix passed in as a numpy array
        B: (h x n) matrix passed in as a numpy array

    Returns:
        C: (m x n) matrix as a numpy array
    """
    C = []
    for i in range(m):
        C_row = []
        for j in range(n):
            temp_sum = 0
            for k in range(h):
                temp_sum += A[i][k] * B[k][j]
            C_row.append(temp_sum)
        C.append(C_row)
    return C