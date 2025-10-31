import numpy as np
import argparse
import time


def bruteforce(m, h, n, A, B):
    """
    Args:
        A: (m x h) matrix passed in as a 2D numpy array
        B: (h x n) matrix passed in as a 2D numpy array
 
    Returns:
        C: (m x n) matrix as a 2D numpy array
    """
    # TODO: Implement the basic O(n^3) runtime matrix multiplication algorithm using what you already know from basic linear algebra!
    C = None
    for i in range(m):
        for j in range(n):
            for k in range(h):
                pass
    return C