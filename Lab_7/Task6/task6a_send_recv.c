#include <stdio.h>
#include <math.h>
#include <mpi.h>

#define LOW  2
#define HIGH 10000000

int isPrime(int n)
{
    if (n < 2)
        return 0;
    if (n % 2 == 0)
        return n == 2;
    int limit = (int)sqrt((double)n);
    for (int d = 3; d <= limit; d += 2)
        if (n % d == 0)
            return 0;
    return 1;
}

int main(int argc, char **argv)
{
    int rank, size;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    double t0 = MPI_Wtime();

    // split [LOW, HIGH] into size blocks; the last one takes any leftover
    int total = HIGH - LOW + 1;
    int block = total / size;
    int start = LOW + rank * block;
    int end = (rank == size - 1) ? HIGH : start + block - 1;

    int local = 0;
    for (int n = start; n <= end; n++)
        if (isPrime(n))
            local++;

    printf("Process %d: [%d, %d] has %d primes\n", rank, start, end, local);

    if (rank != 0) {
        MPI_Send(&local, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
    } else {
        int count = local;
        for (int src = 1; src < size; src++) {
            int c;
            MPI_Recv(&c, 1, MPI_INT, src, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            count += c;
        }
        printf("\nNumber of primes between %d and %d: %d\n", LOW, HIGH, count);
        printf("Time: %.3f s\n", MPI_Wtime() - t0);
    }

    MPI_Finalize();
    return 0;
}
