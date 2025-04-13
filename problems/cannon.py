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

    # Create blocks of A and B
    if cart_rank == 0:
        A_blocks = np.empty((size, block_size, block_size), dtype=A.dtype)
        B_blocks = np.empty((size, block_size, block_size), dtype=B.dtype)
        idx = 0
        for i in range(q):
            for j in range(q):
                # These 2 lines create the blocks and ensure each block is contiguous so that they can be distributed
                A_blocks[idx] = np.ascontiguousarray(A[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size])
                B_blocks[idx] = np.ascontiguousarray(B[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size])
                idx += 1
    else:
        A_blocks = None
        B_blocks = None

    # TODO: Distribute the blocks of A and B to all other processes.
    # This requires 1 MPI instruction for the A blocks and 1 MPI instruction for the B blocks




    # These first 2 loops are to move the blocks to their starting positions 
    # First, shift blocks of A to the left.
    # Hint for below: coords[0] is the row coordinate, coords[1] is the column coordinate
    for step in range(0):
        left_coords = (0, 0) # TODO: Calculate the coordinates of the left neighbor (to send to).
        right_coords = (0, 0) # TODO: Calculate the coordinates of the right neighbor (to receive from).
        left_rank = comm_cart.Get_cart_rank(left_coords)
        right_rank = comm_cart.Get_cart_rank(right_coords)
        comm_cart.Sendrecv_replace(local_A, dest=left_rank, sendtag=0, source=right_rank, recvtag=0)
    
    # Second, shift blocks of B up.
    for step in range(0):
        up_coords = (0, 0) # TODO: Calculate the coordinates of the upper neighbor (to send to).
        down_coords = (0, 0) # TODO: Calculate the coordinates of the lower neighbor (to receive from).
        up_rank = comm_cart.Get_cart_rank(up_coords)
        down_rank = comm_cart.Get_cart_rank(down_coords)
        comm_cart.Sendrecv_replace(local_B, dest=up_rank, sendtag=1, source=down_rank, recvtag=1)

    # With the blocks shifted, the matrix multiplication can now proceed.
    # np.dot(A, B) performs the matrix multiplication for the blocks that are possessed. The resulting values are then added to the current C.
    for step in range(0):
        # Multiply and accumulate
        local_C += np.dot(local_A, local_B)

        # Shift the local block of A to the left.
        left_coords = 0 # TODO: Calculate the coordinates of the left neighbor (to send to).
        right_coords = 0 # TODO: Calculate the coordinates of the right neighbor (to receive from).
        left_rank = comm_cart.Get_cart_rank(left_coords)
        right_rank = comm_cart.Get_cart_rank(right_coords)
        comm_cart.Sendrecv_replace(local_A, dest=left_rank, sendtag=2, source=right_rank, recvtag=2)

        # Shift the local block of B up.
        up_coords = 0 # TODO: Calculate the coordinates of the upper neighbor (to send to).
        down_coords = 0 # TODO: Calculate the coordinates of the lower neighbor (to receive from).
        up_rank = comm_cart.Get_cart_rank(up_coords)
        down_rank = comm_cart.Get_cart_rank(down_coords)
        comm_cart.Sendrecv_replace(local_B, dest=up_rank, sendtag=3, source=down_rank, recvtag=3)

    # Send all local_C blocks to the root process.
    collected_C = None
    if cart_rank == 0:
        collected_C = np.empty((size, block_size, block_size), dtype=local_C.dtype)
    
    # TODO: Add an MPI instruction to get all of the blocks back to the root (process 0).



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
