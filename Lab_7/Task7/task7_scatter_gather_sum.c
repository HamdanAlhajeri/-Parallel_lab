#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

#define PER_PROC 5      // numbers each process gets

int main(int argc, char **argv)
{
    int rank, size;
    int *numbers = NULL;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int n = PER_PROC * size;

    // 1. root generates the random array
    if (rank == 0) {
        srand((unsigned)time(NULL));
        numbers = malloc(n * sizeof(int));
        printf("Root generated %d numbers:", n);
        for (int i = 0; i < n; i++) {
            numbers[i] = rand() % 100 + 1;   // 1..100
            printf(" %d", numbers[i]);
        }
        printf("\n\n");
    }

    // 2. scatter an equal share to every process
    int local[PER_PROC];
    MPI_Scatter(numbers, PER_PROC, MPI_INT, local, PER_PROC, MPI_INT, 0, MPI_COMM_WORLD);

    // 3. each process sums its own part
    int local_sum = 0;
    for (int i = 0; i < PER_PROC; i++)
        local_sum += local[i];
    printf("Process %d got {%d, %d, %d, %d, %d}, local sum = %d\n",
           rank, local[0], local[1], local[2], local[3], local[4], local_sum);

    // 4. gather all partial sums on the root
    int *sums = NULL;
    if (rank == 0)
        sums = malloc(size * sizeof(int));
    MPI_Gather(&local_sum, 1, MPI_INT, sums, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        int total = 0;
        printf("\nRoot gathered partial sums:");
        for (int r = 0; r < size; r++) {
            printf(" %d", sums[r]);
            total += sums[r];
        }
        printf("\nFinal sum = %d\n", total);

        // check against a plain serial sum
        int check = 0;
        for (int i = 0; i < n; i++)
            check += numbers[i];
        printf("Serial check = %d (%s)\n", check, check == total ? "match" : "MISMATCH");

        free(sums);
        free(numbers);
    }

    MPI_Finalize();
    return 0;
}
