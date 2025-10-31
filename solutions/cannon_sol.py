from mpi4py import MPI
import numpy as np

def cannon_matrix_multiply(A, B, N):
    comm = MPI.COMM_WORLD
    
    rank = comm.Get_rank()
    size = comm.Get_size()

    n = N
    q = int(np.sqrt(size))

    # size must be a perfect square. q should divide n so that each process has the same size block.
    assert q*q == size
    assert n % q == 0

    block_size = n // q

    if rank == 0:
        if A is None or B is None:
            mat_dtype = np.float64
        else:
            mat_dtype = A.dtype
    else:
        mat_dtype = None

    mat_dtype = comm.bcast(mat_dtype, root=0)

    # Create local blocks. Each process receives a block_size * block_size square.
    local_A = np.empty((block_size, block_size), dtype=mat_dtype)
    local_B = np.empty((block_size, block_size), dtype=mat_dtype)
    local_C = np.zeros((block_size, block_size), dtype=mat_dtype)

    # Define the Cartesian communicator. The processes are laid out into a 2D grid, the period indicates wrap-around.
    dims = [q, q]
    periods = [1, 1]
    comm_cart = comm.Create_cart(dims, periods, reorder=True)

    # Ranks can be reordered if that can help improve communication, so the rank in the communication may differ from the original
    cart_rank = comm_cart.Get_rank()
    coords = comm_cart.Get_coords(cart_rank)

    # Scatter blocks of A and B
    if cart_rank == 0:
        A_blocks = np.empty((size, block_size, block_size), dtype=A.dtype)
        B_blocks = np.empty((size, block_size, block_size), dtype=B.dtype)
        idx = 0
        for i in range(q):
            for j in range(q):
                # These 2 lines create the blocks and ensure each block is contiguous so that they can be scattered
                A_blocks[idx] = np.ascontiguousarray(A[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size])
                B_blocks[idx] = np.ascontiguousarray(B[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size])
                idx += 1
    else:
        A_blocks = None
        B_blocks = None

    comm_cart.Scatter(A_blocks, local_A, root=0)
    comm_cart.Scatter(B_blocks, local_B, root=0)

    # These first 2 loops are to move the blocks to their starting positions 
    # First, shift blocks of A to the left. The shift equals the row coordinate. The farther down the row is, the more it is shifted left.
    for step in range(coords[0]):
        # Destination: left neighbor (same row, column-1 mod q)
        # Source: right neighbor (same row, column+1 mod q)
        left_coords = (coords[0], (coords[1] - 1) % q)
        right_coords = (coords[0], (coords[1] + 1) % q)
        left_rank = comm_cart.Get_cart_rank(left_coords)
        right_rank = comm_cart.Get_cart_rank(right_coords)
        comm_cart.Sendrecv_replace(local_A, dest=left_rank, sendtag=0, source=right_rank, recvtag=0)
    
    # Second, shift blocks of B up. The shift equals the column coordinate. The farther to the right the column is, the more it is shifted up.
    for step in range(coords[1]):
        # Destination: up neighbor (row-1 mod q, same column)
        # Source: down neighbor (row+1 mod q, same column)
        up_coords = ((coords[0] - 1) % q, coords[1])
        down_coords = ((coords[0] + 1) % q, coords[1])
        up_rank = comm_cart.Get_cart_rank(up_coords)
        down_rank = comm_cart.Get_cart_rank(down_coords)
        comm_cart.Sendrecv_replace(local_B, dest=up_rank, sendtag=1, source=down_rank, recvtag=1)

    # With the blocks shifted, the matrix multiplication can now proceed.
    # np.dot(A, B) performs the matrix multiplication for the blocks that are possessed. The resulting values are then added to the current C.
    for step in range(q):
        # Multiply and accumulate
        local_C += np.dot(local_A, local_B)

        # Shift the local block of A to the left.
        left_coords = (coords[0], (coords[1] - 1) % q)
        right_coords = (coords[0], (coords[1] + 1) % q)
        left_rank = comm_cart.Get_cart_rank(left_coords)
        right_rank = comm_cart.Get_cart_rank(right_coords)
        comm_cart.Sendrecv_replace(local_A, dest=left_rank, sendtag=2,
                                     source=right_rank, recvtag=2)

        # Shift the local block of B up.
        up_coords = ((coords[0] - 1) % q, coords[1])
        down_coords = ((coords[0] + 1) % q, coords[1])
        up_rank = comm_cart.Get_cart_rank(up_coords)
        down_rank = comm_cart.Get_cart_rank(down_coords)
        comm_cart.Sendrecv_replace(local_B, dest=up_rank, sendtag=3, source=down_rank, recvtag=3)

    # Gather all local_C blocks back to the root process.
    collected_C = None
    if cart_rank == 0:
        collected_C = np.empty((size, block_size, block_size), dtype=local_C.dtype)
    comm_cart.Gather(local_C, collected_C, root=0)

    # Process 0 combines all of the block of C into 1 result matrix.
    if cart_rank == 0:
        result = np.empty((n, n), dtype=local_C.dtype)
        idx = 0
        for i in range(q):
            for j in range(q):
                result[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size] = collected_C[idx]
                idx += 1
        return result
    return None
