#include <pthread.h>
#include <stdio.h>

volatile int x = 0;
volatile int y = 0;

pthread_mutex_t lock;   // protects x, y and the printf calls

void *func1(void *arg)
{
    int z = 0;

    pthread_mutex_lock(&lock);
    y++;
    z = 5;
    printf("Hello from func1: x,y,z is %d,%d,%d.\n", x, y, z);
    pthread_mutex_unlock(&lock);

    return NULL;
}

void func2()
{
    int z = 7;

    pthread_mutex_lock(&lock);
    x = 2;
    printf("Hello from func2: y is %d, z is %d.\n", y, z);
    pthread_mutex_unlock(&lock);
}

int main(void)
{
    pthread_t t;

    pthread_mutex_init(&lock, NULL);

    // new thread runs func1, main thread runs func2
    pthread_create(&t, NULL, func1, NULL);
    func2();

    // wait for the new thread to finish
    pthread_join(t, NULL);

    pthread_mutex_destroy(&lock);
    return 0;
}
