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
    comm = None
    world_size = None
    print(f"The size of the world is {world_size}")
    rank = None
    print(f"Hello world from processor {rank}!\n")

def greetings_between_friends():
    """
    Processors rank 0 and rank 1 are friends. For Christmas, processor 1
    requested a "Hello World" package from rank 0. Help processor 0 send
    their gift to rank 1 and ensure that rank 1 receives it!
    """
    comm = None
    rank = None
    if rank == 0:
        pass
    elif rank == 1:
        data = None
        print(f"Processor {rank} received gift {data}!")
        pass

def greetings_between_all_friends():
    """
    All other friends are now jealous that processor 1 has received a gift
    while they did not receive any. Make sure that processor 0 not sends
    another "Sorry" package to all other processors, including processor 1.
    """
    raise NotImplementedError

def be_a_more_considerate_friend():
    """
    Honestly, sending the same thing to everyone is lazy as hell. Processor 2
    thinks that processor 0 is being a bad friend. For Christmas, processor 2
    created a list of packages, each unique in their own way. It wants to 
    distribute their gifts so that each friend receives only 1 gift. Help
    processor 2 distribute their gifts!
    """
    raise NotImplementedError

def santas_pipeline():
    """
    Santa operates a sleigh factory for the 
    """

def santas_accounts():
    """
    Every week, Santa counts up how much he's made in total from all
    the elves helping him sell his sleighs. Get the total amount that
    Santa has made this week from all the sleighs that his elves has sold.
    """
    raise NotImplementedError

def pipping_at_the_northpole():
    """
    Its the end of Christmas and Santa is now counting up how much each elf
    has earned from sales. The worst performing elf WILl BE PIPPED. Help Santa 
    total up how much each elf has earned and find the elf that will be fired :)
    """
    raise NotImplementedError

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
    comm = None
    rank = None
    elf_earnings = [random.uniform(1, 4) for _ in random.randint(1,10)] 
    total_earned = None
    all_totals = None
    print(f"Elf {rank} has {all_totals} amount of money! Viva la revolution!")

if __name__=="__main__":
    learn_about_the_world()
    greetings_between_friends()
    greetings_between_all_friends()
    be_a_more_considerate_friend()
    santas_pipeline()
    santas_accounts()
    pipping_at_the_northpole()
    elf_revolution()