# Spring25-Workshop2-Optimization

Repository containing materials for the Spring 2025 workshop 2 on matrix multiplication optimization.

## Installation & Environment Setup

1. Clone repository to working environment. 
2. `cd` into the directory and run `chmod +x *.sh`.
3. Run `./get_nodes.sh [num_nodes]` to allocate nodes on the cluster for 3 hours. Default `num_nodes` is 4. Allocate more cores to test some of the larger matrices!
4. `module load anaconda3`
5. Create conda environment: `conda create --name sp25_suco2 -c conda-forge python=3.11 numpy openmpi mpi4py -y`
6. `conda activate sp25_suco2`
7. Test if mpi4py is working for you successfully by running `./run.sh test`.

## Option 1: Testing Intro to MPI

1. Fill out the file `problems/0-mpi-intro.py` to familiarize yourself with MPI4Py. There is no existing test file for the program, so as you complete each function, make sure that the printed output matches the problem description described in the comment under each function.
2. Run the file using the command `./run.sh intro`.

## Option 2: Testing Matrix Multiplication Functions

1. The driver file that will parse the input files storing the complete information of matrices (stored in `tests/`) and run your completed optimized matrix-multiplication functions is `main.py`. 
2. Implement the matrix-multiplication functions using the files under the directory `problems/`. The solutions are under the directory `solutions/`.
3. You can test each function individually as you complete them or test all the functions at once using `./run.sh [command]`. The available commands are listed below:
    ```bash
    ./run.sh brute
    ./run.sh blocked
    ./run.sh cannon
    ./run.sh spgemm

    ./run.sh test_all_small     # Tests all functions using matrices of size (11 x 11)
    ./run.sh test_all_med       # Tests all functions using matrices of size (9914 x 9914)
    ./run.sh test_all_large     # Tests all functions using matrices of size (77360 x 77360)
    ```
4. BONUS: We mentioned that we can also implemented Gustavson's sparse matrix multiplication algorithm using the **compressed sparse row (CSR)** data structure to further optimize matrix multiplication. Unfortunately, Santa got drunk the day before this workshop and their huge migraine meant that they could not complete the function in time. Try to complete this function on your own time and comment out the lines that tests this version of SPGEMM from `run.sh` to compare the runtime of SPGEMM when different data structures are used!