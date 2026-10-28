#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv)
{
    int rank, size;
    int number;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (rank == 0) {
        // rank 0 comes up with the number and starts the chain
        number = 7;
        printf("Process 0 starts the game with number %d\n", number);
        if (size > 1)
            MPI_Send(&number, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
    } else {
        // receive FIRST from the previous rank, THEN pass it on;
        // a rank cannot send a number it has not received yet
        MPI_Recv(&number, 1, MPI_INT, rank - 1, 0, MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
        printf("Process %d received %d from process %d\n",
               rank, number, rank - 1);
        if (rank < size - 1)
            MPI_Send(&number, 1, MPI_INT, rank + 1, 0, MPI_COMM_WORLD);
    }

    MPI_Finalize();
    return 0;
}
