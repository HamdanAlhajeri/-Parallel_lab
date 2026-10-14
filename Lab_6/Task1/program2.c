#include <pthread.h>
#include <stdio.h>

int counter;   // shared, but only one thread runs at a time here

void *thread_func(void *arg)
{
    int i;
    for (i = 0; i < 100000; i++)
        counter++;
    return NULL;
}

int main(void)
{
    int i, N = 5;
    pthread_t t[N];

    // create a thread and wait for it right away,
    // so the next thread only starts after the previous one is done
    for (i = 0; i < N; i++) {
        pthread_create(&t[i], NULL, thread_func, NULL);
        pthread_join(t[i], NULL);
    }

    printf("%d\n", counter);
    return 0;
}
