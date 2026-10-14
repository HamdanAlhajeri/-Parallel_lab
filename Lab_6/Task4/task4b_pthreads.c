#include <stdio.h>
#include <pthread.h>
#include <time.h>

#define N 2000000

char is_composite[N + 1];   // shared sieve array, 0 = unmarked
int count = 0;              // shared prime count, NOT protected

// endpoints for one thread
typedef struct {
    long start;
    long end;   // inclusive
} Range;

void *sieve_range(void *arg)
{
    Range *r = (Range *)arg;

    // find the sieving primes by scanning the low part of the SHARED array.
    // t2 reads cells that t1 may still be writing -> race on is_composite.
    for (long x = 2; x * x <= r->end; x++) {
        if (!is_composite[x]) {
            // first multiple of x inside this thread's range (and >= x*x)
            long first = ((r->start + x - 1) / x) * x;
            if (first < x * x)
                first = x * x;
            for (long m = first; m <= r->end; m += x)
                is_composite[m] = 1;
        }
    }

    // count primes in this range straight into the shared counter.
    // count++ is not atomic, so the two threads can lose updates.
    for (long i = r->start; i <= r->end; i++)
        if (i >= 2 && !is_composite[i])
            count++;

    pthread_exit(NULL);
}

int main(void)
{
    pthread_t t1, t2;
    Range r1 = {0, 1000000};
    Range r2 = {1000001, 2000000};
    struct timespec a, b;

    clock_gettime(CLOCK_MONOTONIC, &a);

    pthread_create(&t1, NULL, sieve_range, &r1);
    pthread_create(&t2, NULL, sieve_range, &r2);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    clock_gettime(CLOCK_MONOTONIC, &b);
    double secs = (b.tv_sec - a.tv_sec) + (b.tv_nsec - a.tv_nsec) / 1e9;

    printf("Two threads (with race): %d primes between 0 and %d\n", count, N);
    printf("Expected: 148933\n");
    printf("Time: %f seconds\n", secs);
    return 0;
}
