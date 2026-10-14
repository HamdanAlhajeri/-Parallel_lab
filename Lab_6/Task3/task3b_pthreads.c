#include <stdio.h>
#include <math.h>
#include <pthread.h>
#include <time.h>

#define N 100000
#define NUM_THREADS 4

int pcount = 0;                 // shared prime counter
pthread_mutex_t count_lock;     // protects pcount

// endpoints of the range one thread checks
typedef struct {
    int start;
    int end;    // inclusive
} Range;

int isPrime(int n)
{
    if (n < 2)
        return 0;
    int limit = (int)sqrt((double)n);
    for (int d = 2; d <= limit; d++)
        if (n % d == 0)
            return 0;
    return 1;
}

void *count_primes(void *arg)
{
    Range *r = (Range *)arg;

    // count in a local variable first so we only lock once per thread
    int local = 0;
    for (int n = r->start; n <= r->end; n++)
        if (isPrime(n))
            local++;

    pthread_mutex_lock(&count_lock);
    pcount += local;
    pthread_mutex_unlock(&count_lock);

    printf("Thread checked [%d, %d] -> %d primes\n", r->start, r->end, local);
    pthread_exit(NULL);
}

int main(void)
{
    pthread_t threads[NUM_THREADS];
    Range ranges[NUM_THREADS];
    int chunk = (N + 1) / NUM_THREADS;
    struct timespec t0, t1;

    pthread_mutex_init(&count_lock, NULL);
    clock_gettime(CLOCK_MONOTONIC, &t0);

    // split 0..N into equal pieces, one per thread
    for (int i = 0; i < NUM_THREADS; i++) {
        ranges[i].start = i * chunk;
        ranges[i].end = (i == NUM_THREADS - 1) ? N : (i + 1) * chunk - 1;
        pthread_create(&threads[i], NULL, count_primes, &ranges[i]);
    }

    for (int i = 0; i < NUM_THREADS; i++)
        pthread_join(threads[i], NULL);

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;

    printf("Parallel (%d threads): %d primes between 0 and %d\n", NUM_THREADS, pcount, N);
    printf("Time: %f seconds\n", secs);

    pthread_mutex_destroy(&count_lock);
    return 0;
}
