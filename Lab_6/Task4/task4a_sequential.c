#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 2000000

int main(void)
{
    // is_composite[i] == 0 means i is still unmarked (prime candidate)
    char *is_composite = calloc(N + 1, 1);
    clock_t start = clock();

    is_composite[0] = is_composite[1] = 1;   // 0 and 1 are not prime

    // pick the smallest unmarked x and mark its multiples, while x*x <= N
    for (long x = 2; x * x <= N; x++) {
        if (!is_composite[x]) {
            for (long m = x * x; m <= N; m += x)
                is_composite[m] = 1;
        }
    }

    int count = 0;
    for (int i = 0; i <= N; i++)
        if (!is_composite[i])
            count++;

    double secs = (double)(clock() - start) / CLOCKS_PER_SEC;
    printf("Sequential sieve: %d primes between 0 and %d\n", count, N);
    printf("Time: %f seconds\n", secs);

    free(is_composite);
    return 0;
}
