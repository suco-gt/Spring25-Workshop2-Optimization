# Spring25-Workshop2-Optimization

Repository containing materials for the Spring 2025 workshop 2 on matrix multiplication optimization.

## Installation & Environment Setup

1. Clone repository to working environment. 
2. Run `bash get_nodes.sh [num_nodes]` to allocate nodes on the cluster for 1 hour. Default `num_nodes` is 4. 
3. `module load anaconda3`
4. cd into directory and install conda environment: `conda env create -f environment.yml -y`
5. `conda activate sp25_suco2`
6. Test if mpi4py is working for you successfully by running `bash run.sh test`.


