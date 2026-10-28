#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, size;
    int number = 0;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (rank == 0) {
        number = 7;
        printf("Process 0 starts the game with number %d\n", number);
    }

    // one collective call replaces the whole Send/Recv chain;
    // every rank calls it, rank 0 is the root that sends
    MPI_Bcast(&number, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank != 0)
        printf("Process %d received %d\n", rank, number);

    MPI_Finalize();
    return 0;
}
