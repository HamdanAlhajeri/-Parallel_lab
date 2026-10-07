#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define N 10000000   // how many random points we throw

int main(void) {
    long hits = 0;
    int nthreads = 0;

    // start the threads; each one keeps its own hits count
    #pragma omp parallel reduction(+:hits)
    {
        int id = omp_get_thread_num();   // which thread am I
        unsigned int seed = 1234 + id;   // each thread gets a different seed

        if (id == 0)
            nthreads = omp_get_num_threads();   // save how many threads there are

        // split the loop between the threads
        #pragma omp for
        for (int i = 0; i < N; i++) {
            double x = (double)rand_r(&seed) / RAND_MAX;   // random x from 0 to 1
            double y = (double)rand_r(&seed) / RAND_MAX;   // random y from 0 to 1
            if (x * x + y * y <= 1.0)
                hits++;   // point landed inside the circle
        }
    }   // all the threads' hits get added together here

    double pi = 4.0 * hits / N;

    printf("Threads     : %d\n", nthreads);
    printf("Points      : %d\n", N);
    printf("Hits        : %ld\n", hits);
    printf("Estimated PI: %f\n", pi);

    return 0;
}