#include <pthread.h>
#include <stdio.h>

int counter;   // shared by all threads, no lock

void *thread_func(void *arg)
{
    int i;
    for (i = 0; i < 100000; i++)
        counter++;   // read-modify-write, not atomic -> data race
    return NULL;
}

int main(void)
{
    int i, N = 5;
    pthread_t t[N];

    // start all 5 threads first, so they run at the same time
    for (i = 0; i < N; i++)
        pthread_create(&t[i], NULL, thread_func, NULL);

    // then wait for all of them
    for (i = 0; i < N; i++)
        pthread_join(t[i], NULL);

    printf("%d\n", counter);
    return 0;
}
