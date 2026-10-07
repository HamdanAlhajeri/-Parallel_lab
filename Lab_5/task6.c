#include <stdio.h>
#include <omp.h>

#define N_A 10
#define N_B 1000000

/* ---------- Task 6(a) ---------- */
void task6a(void) {
    int i, results[N_A];

    // each loop step doesn't need the others, so threads can share the work
    #pragma omp parallel for
    for (i = 0; i < N_A; i++) {
        results[i] = (i + 1) * (i + 1);
    }

    // print normally so the numbers come out in order
    for (i = 0; i < N_A; i++) {
        printf("%d ", results[i]);
    }
    printf("\n");
}

/* ---------- Task 6(b) ---------- */
void task6b(void) {
    float x, sum, step, pi;
    int i;

    sum = 0.0f;
    step = 1.0 / N_B;

    // private(x): each thread gets its own x
    // reduction(+:sum): each thread adds to its own sum, then they get added up at the end
    #pragma omp parallel for private(x) reduction(+:sum)
    for (i = 0; i < N_B; i++) {
        x = (i + 0.5f) * step;
        sum += 4.0 / (1.0 + x * x);
    }

    pi = step * sum;
    printf("pi = %f\n", pi);
}

int main(void) {
    printf("Task 6(a):\n");
    task6a();

    printf("\nTask 6(b):\n");
    task6b();

    return 0;
}