#include <stdio.h>
#include <mpi.h>

#define NUM_PROCS 4

int main(int argc, char **argv)
{
    int rank, size;
    int data[NUM_PROCS] = {10, 20, 30, 40};   // only used on the root
    int element;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size != NUM_PROCS) {
        if (rank == 0)
            printf("Run this program with %d processes: mpiexec -n %d ...\n",
                   NUM_PROCS, NUM_PROCS);
        MPI_Finalize();
        return 1;
    }

    if (rank == 0)
        printf("Process 0 scatters {%d, %d, %d, %d}\n",
               data[0], data[1], data[2], data[3]);

    // one element of data[] goes to each process (including the root)
    MPI_Scatter(data, 1, MPI_INT, &element, 1, MPI_INT, 0, MPI_COMM_WORLD);

    printf("Process %d received element %d\n", rank, element);

    MPI_Finalize();
    return 0;
}
