#include <stdio.h>
#include <pthread.h>
#include <time.h>

#define N 2000000
#define SQRT_N 1415   // sqrt(2,000,000) ~ 1414.2

char is_composite[N + 1];   // shared sieve array, threads write disjoint ranges
int base_primes[SQRT_N];    // primes <= sqrt(N), read-only once threads start
int num_base = 0;

int count = 0;               // shared prime count
pthread_mutex_t count_lock;  // protects count

typedef struct {
    long start;
    long end;   // inclusive
    int local;  // primes found by this thread
} Range;

void *sieve_range(void *arg)
{
    Range *r = (Range *)arg;

    // only use the read-only base primes, never read the other thread's cells
    for (int k = 0; k < num_base; k++) {
        long p = base_primes[k];
        if (p * p > r->end)
            break;
        long first = ((r->start + p - 1) / p) * p;
        if (first < p * p)
            first = p * p;
        for (long m = first; m <= r->end; m += p)
            is_composite[m] = 1;   // only cells inside [start, end]
    }

    // count into a private variable
    int local = 0;
    for (long i = r->start; i <= r->end; i++)
        if (i >= 2 && !is_composite[i])
            local++;
    r->local = local;

    // one locked update to the shared counter
    pthread_mutex_lock(&count_lock);
    count += local;
    pthread_mutex_unlock(&count_lock);

    pthread_exit(NULL);
}

int main(void)
{
    pthread_t t1, t2;
    Range r1 = {0, 1000000, 0};
    Range r2 = {1000001, 2000000, 0};
    struct timespec a, b;

    pthread_mutex_init(&count_lock, NULL);
    clock_gettime(CLOCK_MONOTONIC, &a);

    // step 1 (sequential): small sieve to get the primes up to sqrt(N)
    char small[SQRT_N + 1] = {0};
    for (int x = 2; x <= SQRT_N; x++) {
        if (!small[x]) {
            base_primes[num_base++] = x;
            for (int m = x * x; m <= SQRT_N; m += x)
                small[m] = 1;
        }
    }

    // step 2 (parallel): each thread sieves its own half
    pthread_create(&t1, NULL, sieve_range, &r1);
    pthread_create(&t2, NULL, sieve_range, &r2);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    clock_gettime(CLOCK_MONOTONIC, &b);
    double secs = (b.tv_sec - a.tv_sec) + (b.tv_nsec - a.tv_nsec) / 1e9;

    printf("t1 [0, 1000000]:       %d primes\n", r1.local);
    printf("t2 [1000001, 2000000]: %d primes\n", r2.local);
    printf("Two threads (no race): %d primes between 0 and %d\n", count, N);
    printf("Time: %f seconds\n", secs);

    pthread_mutex_destroy(&count_lock);
    return 0;
}
