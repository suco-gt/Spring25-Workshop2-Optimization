import mpi4py
from mpi4py import MPI
import numpy as np
import argparse
import time

from problems.bruteforce import bruteforce
from problems.spgemm import coo_spgemm, csr_spgemm

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

def distribute_coo(edge_list):
    raise NotImplementedError

if __name__=="__main__":
    parser = argparse.ArgumentParser(prog='Driver code')
    parser.add_argument('-f', '--file', type=str)
    parser.add_argument('-o', '--optim', type=str)
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    num_nodes, src_node, num_edges = 0, 0, 0
    edge_list, spgemm_result = None, None
    if rank == 0:
        num_nodes, src_node, num_edges, edge_list, spgemm_result = read_sparse_matrix_file(args.file)
        data = (num_nodes, src_node, num_edges)
    else:
        data = None
    data = comm.bcast(data, root=0)

    if rank == 0:
        matrix_A = []
        matrix_A_transpose = []
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
            my_C = np.array(bruteforce(num_nodes, num_nodes, num_nodes, square_matrix_A, square_matrix_A_transpose))
            if np.array_equal(my_C, square_spgemm_result):
                print("Resulting matrices match!")
            else:
                print(f"Expected: \n\t{square_spgemm_result}\n\nGot \n\t{my_C}")
    elif args.optim == "tiling":
        pass
    elif args.optim == "cannon":
        pass
    elif args.optim == "spgemm1":
        pass
    elif args.optim == "spgemm2":
        pass
    else:
        print("Invalid optimization method selected.")
    

    # a_send_rows =  np.zeros((size,))
    # b_send_rows =  np.zeros((size,))
    # a_send_indices =  np.zeros((size + 1,))
    # b_send_indices =  np.zeros((size + 1,))
    # c_send_rows =  np.zeros((size,))
    # c_send_indices =  np.zeros((size + 1,))
    # a_rows_to_rank = np.zeros((data[0],))
    # b_rows_to_rank =  np.zeros((data[0],))
    # c_rows_to_rank =  np.zeros((data[0],))

    # a_send_counts = np.zeros((size,))
    # b_send_counts = np.zeros((size,))
    # c_send_counts = np.zeros((size,))
    # a_send_data, b_send_data, c_send_data = [ [] for _ in range(size) ], [ [] for _ in range(size) ], [ [] for _ in range(size) ]

    # for i in range(size):
    #     a_send_rows[i] = data[0] // size
    #     b_send_rows[i] = data[0] // size
    #     c_send_rows[i] = data[0] // size
    #     if data[0] % size > i:
    #         a_send_rows[i] += 1
    #         b_send_rows[i] += 1
    #         c_send_rows[i] += 1
    
    # if rank == 0:
    #     a_send_indices[0] = 0
    #     b_send_indices[0] = 0
    #     c_send_indices[0] = 0

    #     for i in range(1, size + 1):
    #         a_send_indices[i] = a_send_indices[i - 1] + a_send_rows[i - 1]
    #         b_send_indices[i] = b_send_indices[i - 1] + b_send_rows[i - 1]
    #         c_send_indices[i] = c_send_indices[i - 1] + c_send_rows[i - 1]
        
    #     for i in range(size):
    #         for j in range(int(a_send_indices[i]), int(a_send_indices[i + 1])):
    #             a_rows_to_rank[j] = i
    #         for j in range(int(b_send_indices[i]), int(b_send_indices[i + 1])):
    #             b_rows_to_rank[j] = i
    #         for j in range(int(c_send_indices[i]), int(c_send_indices[i + 1])):
    #             c_rows_to_rank[j] = i

    #     a_rows_to_rank = a_rows_to_rank.astype(int) 
    #     b_rows_to_rank = b_rows_to_rank.astype(int) 
    #     c_rows_to_rank = c_rows_to_rank.astype(int)

    #     for idx, A_el in enumerate(matrix_A):
    #         a_send_data[a_rows_to_rank[A_el[0]]].append(A_el)
        
    #     for idx, A_t_el in enumerate(matrix_A_transpose):
    #         b_send_data[b_rows_to_rank[A_t_el[0]]].append(A_t_el)

    #     for idx, res_el in enumerate(spgemm_result):
    #         c_send_data[c_rows_to_rank[res_el[0]]].append(res_el)

    # a_data_recvbuf = comm.scatter(a_send_data, root=0)
    # b_data_recvbuf = comm.scatter(b_send_data, root=0)
    # c_data_recvbuf = comm.scatter(c_send_data, root=0)

    # start = time.perf_counter()
    # C_computed = coo_spgemm(num_nodes, num_nodes, num_nodes, a_data_recvbuf, b_data_recvbuf)
    # end = time.perf_counter()

    # if rank == 0:
    #     print(f"Time Taken for multiplying matrices of size ({num_nodes} x {num_nodes}): {end - start:0.4f} seconds")
    #     print(C_computed)