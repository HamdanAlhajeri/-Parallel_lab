#include <stdio.h>
#include <math.h>
#include <time.h>
#include <mpi.h>

#define TOTAL_POINTS 100000000LL

// small 64-bit xorshift generator so every process has its own stream
// (rand() is shared state and only has 15 bits on Windows)
static unsigned long long rng_state;

double rand01(void)
{
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return (rng_state >> 11) * (1.0 / 9007199254740992.0);   // [0, 1)
}

int main(int argc, char **argv)
{
    int rank, size;
    const double PI_REF = 3.14159265358979323846;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    double t0 = MPI_Wtime();

    // each process throws its share of the darts (last one takes the leftover)
    long long my_points = TOTAL_POINTS / size;
    if (rank == size - 1)
        my_points += TOTAL_POINTS % size;

    rng_state = 88172645463325252ULL ^ ((unsigned long long)time(NULL) * 2654435761ULL)
                ^ ((unsigned long long)(rank + 1) << 32);

    // count points (x, y) in the unit square that fall inside the quarter circle
    long long my_hits = 0;
    for (long long i = 0; i < my_points; i++) {
        double x = rand01();
        double y = rand01();
        if (x * x + y * y <= 1.0)
            my_hits++;
    }

    printf("Process %d: %lld of %lld points inside the circle\n", rank, my_hits, my_points);

    long long hits = 0;
    MPI_Reduce(&my_hits, &hits, 1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        // area of quarter circle / area of square = pi / 4
        double pi = 4.0 * (double)hits / (double)TOTAL_POINTS;
        printf("\nPoints: %lld, inside: %lld\n", TOTAL_POINTS, hits);
        printf("Estimated PI = %.8f\n", pi);
        printf("Error        = %.8f\n", fabs(pi - PI_REF));
        printf("Time: %.3f s\n", MPI_Wtime() - t0);
    }

    MPI_Finalize();
    return 0;
}
