import mpi4py
from mpi4py import MPI
import random

"""
All functions that will be used are contained within the documentation for mpi4py:
    https://mpi4py.readthedocs.io/en/stable/overview.html

For more in-depth information about MPI (if you are not scared of a little bit of C), 
    visit: https://rantahar.github.io/introduction-to-mpi/!
"""

def learn_about_the_world():
    """
    In MPI, processes are organized into groups. Depending on the use case, 
    we may want to split the "entire world" of processes (MPI.COMM_WORLD)
    into multiple groups. However, throughout this entire seminar we will
    consider the entire world as our oyster. 

    Get the size of our world (i.e., number of processes) and say hello
    from each processor (identify each processor using its unique ID)!
    """
    comm = MPI.COMM_WORLD
    world_size = comm.Get_size()
    rank = comm.Get_rank()
    if rank == 0:
        print(f"The size of the world is {world_size}")
    print(f"Hello world from processor {rank}!")


def greetings_between_friends():
    """
    Processors rank 0 and rank 1 are friends. For Christmas, processor 1
    requested a "Hello World" package from rank 0. Help processor 0 send
    their gift to rank 1 and ensure that rank 1 receives it!
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        comm.send("Hello World", dest=1, tag=0)
    elif rank == 1:
        data = comm.recv(source=0, tag=0)
        print(f"Processor {rank} received gift {data}!")

def greetings_between_all_friends():
    """
    All other friends are now jealous that processor 1 has received a gift
    while they did not receive any. Make sure that processor 0 not sends
    another "Sorry" package to all other processors, including processor 1.
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        data = "Sorry"
    else:
        data = None
    data = comm.bcast(data, root=0)
    if rank != 0:
        print(f"Processor {rank} received {data} from processor 0!")

def be_a_more_considerate_friend():
    """
    Honestly, sending the same thing to everyone is lazy as hell. Processor 2
    thinks that processor 0 is being a bad friend. For Christmas, processor 2
    created a list of packages, each unique in their own way. It wants to 
    distribute their gifts so that each friend receives only 1 gift. Help
    processor 2 distribute their gifts!
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 2:
        data = [f"Gift_{i}" for i in range(comm.Get_size())]
    else:
        data = None
    data = comm.scatter(data, root=2)
    if rank != 2:
        print(f"Processor {rank} received {data} from Processor 2!")

def santas_pipeline():
    """
    Santa operates a sleigh factory in the North Pole. He learnt how to operate
    his factory most efficiently from Henry Ford, who taught him that he should
    pipeline his operations. Therefore, each elf in the factory only works on 
    a single part of the sleigh. To construct the final sleigh, the boss elf
    gets a part from each elf. Guide the boss elf through their first time
    working in the pipeline so that they could construct one sleigh!
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    data = rank
    data = comm.gather(data, root=0)
    if rank == 0:
        if len(data) != comm.Get_size():
            print(f"Boss elf is missing some parts! {data}")
        else:
            print(f"Boss elf got all the parts: {data} from {comm.Get_size()} elves!")

def santas_accounts():
    """
    Every week, Santa counts up how much he's made in total from all
    the elves helping him sell his sleighs. Get the total amount that
    Santa has made this week from all the sleighs that his elves has sold.
    """
    random.seed(42)
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank != 0:
        elf_earnings = [random.uniform(1, 4) for _ in range(random.randint(1,10))]
    
    total_earned = 0
    if rank != 0:
        total_earned = sum(elf_earnings)
    
    total = comm.reduce(total_earned, root=0, op=MPI.SUM)
    if rank == 0:
        print(f"Santa has earned {total} amount of money!")
    

def pipping_at_the_northpole():
    """
    Its the end of Christmas and Santa is now counting up how much each elf
    has earned from sales. The worst performing elf WILl BE PIPPED. Help Santa 
    total up how much each elf has earned and find the elf that will be fired :)
    """
    random.seed(42)
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank != 0:
        elf_earnings = [random.uniform(1, 4) for _ in range(random.randint(1,10))]
    
    # Calculate how much each elf has made
    total_earned = float('inf')
    if rank != 0:
        total_earned = sum(elf_earnings)
    
    all_totals = comm.gather(total_earned, root=0)
    if rank == 0:
        print(f"The elf that will be pipped is: {all_totals.index(min(all_totals))}")

def elf_revolution():
    """
    Due to Santa's draconian PIPping practices, the elves are considering a
    revolution. They want to defeat the old status quo and believe that every
    single elf should have access to the entire pool of all of their profits.
    Total up the amount of money each elf made, pool all the money together,
    and make sure that each elf has access to the same amount of money to
    help with their revolution. 
    """
    random.seed(42)
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    elf_earnings = [random.uniform(1, 4) for _ in range(random.randint(1,10))]
    total_earned = sum(elf_earnings)
    all_totals = comm.allreduce(total_earned, op=MPI.SUM)
    print(f"Elf {rank} has {all_totals:.2f} amount of money! Viva la revolution!")


if __name__=="__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    learn_about_the_world()
    if rank == 0: print()
    comm.Barrier()
    
    greetings_between_friends()
    if rank == 0: print()
    comm.Barrier()

    greetings_between_all_friends()
    if rank == 0: print()
    comm.Barrier()

    be_a_more_considerate_friend()
    if rank == 0: print()
    comm.Barrier()

    santas_pipeline()
    if rank == 0: print()
    comm.Barrier()

    santas_accounts()
    if rank == 0: print()
    comm.Barrier()

    pipping_at_the_northpole()
    if rank == 0: print()
    comm.Barrier()

    elf_revolution()