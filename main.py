import mpi4py
from mpi4py import MPI
import numpy as np
import argparse
import time
import math

from solutions.bruteforce import bruteforce
from solutions.spgemm import coo_spgemm, csr_spgemm
from solutions.cannon import cannon_matrix_multiply
from solutions.blocked import blocked_matrix_multiply

def read_sparse_matrix_file(file):
    with open(file, 'r') as f:
        edge_list = []
        spgemm_result = []
        num_nodes, src_node, num_edges, result_num_nnz = 0, 0, 0, 0
        for idx, line in enumerate(f):
            if idx == 0:
                params = line.strip().split(' ')
                num_nodes = int(params[0])
                src_node = int(params[1])
            elif idx == 1:
                num_edges = int(line.strip())
            elif idx > 1 and idx < 2 + num_edges:
                edge = line.strip().split(' ')
                u, v = int(edge[0]), int(edge[1])
                edge_list.append([u, v])
            elif idx == 2 + num_edges:
                # num non-zero entries in A*A transpose
                result_num_nnz = int(line.strip())
            elif idx > 2 + num_edges and idx <= 2 + num_edges + result_num_nnz:
                nnzs = line.strip().split(' ')
                i, j, w = int(nnzs[0]), int(nnzs[1]), int(nnzs[2])
                spgemm_result.append([i, j, w])
    return num_nodes, src_node, num_edges, edge_list, spgemm_result


def convert_to_matrix(num_nodes, edge_list):
    """
    Args:
        edge_list: list of non-zero matrix entries
        num_nodes: int

    Returns:
        square_matrix: (num_nodes x num_nodes) matrix returned as a numpy array
    """
    square_matrix = np.zeros((num_nodes, num_nodes))
    for edge in edge_list:
        row, col, w = edge[0], edge[1], edge[2]
        square_matrix[row][col] = w
    return square_matrix


def pad_matrix(matrix, q):
    # Used when a matrix needs to be divisible into blocks, so n should be a multiple of sqrt(p)
    n, m = matrix.shape
    if n % q == 0:
        return matrix
    new_n = int(math.ceil(n / q)) * q
    padded_matrix = np.pad(matrix, ((0, new_n - n), (0, new_n - m)), mode='constant', constant_values=0)
    return padded_matrix


def distribute_coo(edge_list):
    a_send_rows =  np.zeros((size,))
    a_send_indices =  np.zeros((size + 1,))
    a_rows_to_rank = np.zeros((data[0],))

    a_send_data = [ [] for _ in range(size) ]

    for i in range(size):
        a_send_rows[i] = data[0] // size
        if data[0] % size > i:
            a_send_rows[i] += 1
    
    if rank == 0:
        a_send_indices[0] = 0
        for i in range(1, size + 1):
            a_send_indices[i] = a_send_indices[i - 1] + a_send_rows[i - 1]
        for i in range(size):
            for j in range(int(a_send_indices[i]), int(a_send_indices[i + 1])):
                a_rows_to_rank[j] = i
        a_rows_to_rank = a_rows_to_rank.astype(int) 
        for A_el in edge_list:
            a_send_data[a_rows_to_rank[A_el[0]]].append(A_el)

    return a_send_data


def test_brute(num_nodes, A, B, expected_C):
    start = time.perf_counter()
    my_C = np.array(bruteforce(num_nodes, num_nodes, num_nodes, A, B))
    end = time.perf_counter()
    if np.array_equal(my_C, expected_C):
        print("Resulting matrices match!")
    else:
        print(f"\nExpected: \n\t{expected_C}\n\nGot: \n\t{my_C}\n")
    if rank == 0:
        print(f"Time Taken for multiplying matrices of size ({num_nodes} x {num_nodes}): {end - start:0.4f} seconds") 


def test_blocked(A, B, expected_C):
    start = time.perf_counter()
    
    if rank == 0:
        N = A.shape[0]
    else:
        N = None
    N = comm.bcast(N, root=0)
    my_C = blocked_matrix_multiply(A, B, N)

    end = time.perf_counter()

    if rank == 0:
        if np.array_equal(my_C, expected_C):
            print("Result matrix matches!")
        else:
            print(f"\nExpected: \n\t{expected_C}\n\nGot: \n\t{my_C}\n")
    if rank == 0:
        print(f"Time Taken for multiplying matrices of size ({num_nodes} x {num_nodes}): {end - start:0.4f} seconds")


def test_cannon(A, B, expected_C):
    start = time.perf_counter()
    
    if rank == 0:
        N = A.shape[0]
    else:
        N = None
    N = comm.bcast(N, root=0)
    my_C = cannon_matrix_multiply(A, B, N)

    end = time.perf_counter()

    if rank == 0:
        if np.array_equal(my_C, expected_C):
            print("Result matrix matches!")
        else:
            print(f"\nExpected: \n\t{expected_C}\n\nGot: \n\t{my_C}\n")
    if rank == 0:
        print(f"Time Taken for multiplying matrices of size ({num_nodes} x {num_nodes}): {end - start:0.4f} seconds")


def test_spgemm(A, B, expected_C, kind=1):
    if rank == 0:
        a_send_data = distribute_coo(A)
        b_send_data = distribute_coo(B)
        c_send_data = distribute_coo(expected_C)
    else:
        a_send_data, b_send_data, c_send_data = None, None, None
    
    a_data_recvbuf = comm.scatter(a_send_data, root=0)
    b_data_recvbuf = comm.scatter(b_send_data, root=0)
    c_data_recvbuf = comm.scatter(c_send_data, root=0)

    start = time.perf_counter()
    if kind == 1:
        my_C = coo_spgemm(num_nodes, num_nodes, num_nodes, a_data_recvbuf, b_data_recvbuf)
        my_C = comm.gather(my_C, root=0)
        if rank == 0:
            my_C = [item for sublist in my_C for item in sublist]
    else:
        my_C = csr_spgemm(num_nodes, num_nodes, num_nodes, a_data_recvbuf, b_data_recvbuf)
        my_C = comm.gather(my_C, root=0)
        if rank == 0:
            my_C = [item for sublist in my_C for item in sublist]
    end = time.perf_counter()

    if rank == 0:
        print(f"Time Taken for multiplying matrices of size ({num_nodes} x {num_nodes}): {end - start:0.4f} seconds")
        if my_C == expected_C:
            print("Result matrix matches!")
        else:
            print(f"Expected: \n\n{expected_C}\n\nGot: \n\n{my_C}\n")


if __name__=="__main__":
    parser = argparse.ArgumentParser(prog='Driver code')
    parser.add_argument('-f', '--file', type=str)
    parser.add_argument('-o', '--optim', type=str)
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    num_nodes, src_node, num_edges = 0, 0, 0
    edge_list, spgemm_result = None, []
    if rank == 0:
        num_nodes, src_node, num_edges, edge_list, spgemm_result = read_sparse_matrix_file(args.file)
        data = (num_nodes, src_node, num_edges)
    else:
        data = None
    data = comm.bcast(data, root=0)

    matrix_A = []
    matrix_A_transpose = []    
    if rank == 0:
        for edge in edge_list:
            edge.append(1)
            matrix_A.append(edge)
            matrix_A_transpose.append([edge[1], edge[0], edge[2]])
        matrix_A.sort(key=lambda x: (x[0], x[1]))
        matrix_A_transpose.sort(key=lambda x: (x[0], x[1]))

        square_matrix_A = convert_to_matrix(num_nodes, matrix_A)
        square_matrix_A_transpose = convert_to_matrix(num_nodes, matrix_A_transpose)
        square_spgemm_result = convert_to_matrix(num_nodes, spgemm_result)

    if args.optim == "brute":
        if rank == 0:
            print("=================================Testing Bruteforce Algorithm===============================")
            test_brute(num_nodes, square_matrix_A, square_matrix_A_transpose, square_spgemm_result) 

    elif args.optim == "blocked":
        if rank == 0:
            print("====================Testing Blocked Matrix-Matrix Multiplication Algorithm==================")
        if rank != 0:
            square_matrix_A = None
            square_matrix_A_transpose = None
            square_spgemm_result = None
        else:
            square_matrix_A = pad_matrix(square_matrix_A, int(np.sqrt(size)))
            square_matrix_A_transpose = pad_matrix(square_matrix_A_transpose, int(np.sqrt(size)))
            square_spgemm_result = pad_matrix(square_spgemm_result, int(np.sqrt(size)))
        test_blocked(square_matrix_A, square_matrix_A_transpose, square_spgemm_result)

    elif args.optim == "cannon":
        if rank == 0:
            print("===================Testing Cannon's Matrix-Matrix Multiplication Algorithm=================")
        if rank != 0:
            square_matrix_A = None
            square_matrix_A_transpose = None
            square_spgemm_result = None
        else:
            square_matrix_A = pad_matrix(square_matrix_A, int(np.sqrt(size)))
            square_matrix_A_transpose = pad_matrix(square_matrix_A_transpose, int(np.sqrt(size)))
            square_spgemm_result = pad_matrix(square_spgemm_result, int(np.sqrt(size)))
        test_cannon(square_matrix_A, square_matrix_A_transpose, square_spgemm_result)
    elif args.optim == "spgemm1":
        if rank == 0:
            print("=================Testing Spgemm Matrix-Matrix Multiplication Algorithm w/ COO===============")
        test_spgemm(matrix_A, matrix_A_transpose, spgemm_result, kind=1)

    elif args.optim == "spgemm2":
        if rank == 0:
            print("=================Testing Spgemm Matrix-Matrix Multiplication Algorithm w/ CSR===============")
        test_spgemm(matrix_A, matrix_A_transpose, spgemm_result, kind=2)

    else:
        print("Invalid optimization method selected.")

    

    

    