#include <stdio.h>
#include <math.h>
#include <time.h>

#define N 100000

// returns 1 if n is prime, 0 otherwise
int isPrime(int n)
{
    if (n < 2)
        return 0;
    int limit = (int)sqrt((double)n);
    for (int d = 2; d <= limit; d++)   // try every divisor from 2 to sqrt(n)
        if (n % d == 0)
            return 0;
    return 1;
}

int main(void)
{
    int pcount = 0;
    clock_t start = clock();

    for (int n = 0; n <= N; n++)
        if (isPrime(n))
            pcount++;

    double secs = (double)(clock() - start) / CLOCKS_PER_SEC;
    printf("Sequential: %d primes between 0 and %d\n", pcount, N);
    printf("Time: %f seconds\n", secs);
    return 0;
}
