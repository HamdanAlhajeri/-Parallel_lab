#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

#ifdef _WIN32
#include <windows.h>
#define DELAY() Sleep(100)          // 100 ms per element
#else
#include <unistd.h>
#define DELAY() usleep(100000)
#endif

#define TARGET    50
#define FOUND_TAG 1

// reads whole numbers separated by spaces/new lines; returns the count, -1 on error
int read_data(const char *filename, int **out)
{
    FILE *f = fopen(filename, "r");
    if (f == NULL)
        return -1;

    int cap = 64, n = 0, value;
    int *arr = malloc(cap * sizeof(int));
    while (fscanf(f, "%d", &value) == 1) {
        if (n == cap) {
            cap *= 2;
            arr = realloc(arr, cap * sizeof(int));
        }
        arr[n++] = value;
    }
    fclose(f);

    *out = arr;
    return n;
}

int main(int argc, char **argv)
{
    int rank, size;
    const char *filename = (argc > 1) ? argv[1] : "data.txt";
    int *data = NULL;
    int n = 0;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // master reads the file
    if (rank == 0) {
        n = read_data(filename, &data);
        if (n < 0)
            printf("Cannot open %s\n", filename);
        else if (n == 0 || n % size != 0)
            printf("%s has %d numbers, which is not a multiple of %d processes\n",
                   filename, n, size);
        else
            printf("Master read %d numbers from %s, %d per process\n\n",
                   n, filename, n / size);
    }

    // everyone needs n to know the chunk size (and whether to stop)
    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
    if (n <= 0 || n % size != 0) {
        free(data);
        MPI_Finalize();
        return 1;
    }

    int chunk = n / size;
    int *local = malloc(chunk * sizeof(int));
    MPI_Scatter(data, chunk, MPI_INT, local, chunk, MPI_INT, 0, MPI_COMM_WORLD);

    // post the receive for a "found it" message BEFORE searching
    int msg;                  // global index sent by the finder
    int arrived = 0;
    MPI_Request recv_req;
    MPI_Status status;
    MPI_Irecv(&msg, 1, MPI_INT, MPI_ANY_SOURCE, FOUND_TAG, MPI_COMM_WORLD, &recv_req);

    // start the search on every process at the same time
    MPI_Barrier(MPI_COMM_WORLD);

    int found_at = -1;        // global index if this process finds 50
    int checked = 0;          // how many elements this process looked at
    for (int i = 0; i < chunk; i++) {
        DELAY();
        checked++;
        if (local[i] == TARGET) {
            found_at = rank * chunk + i;
            break;
        }
        MPI_Test(&recv_req, &arrived, &status);
        if (arrived)
            break;            // someone else found it, stop early
    }

    int notified_by = -1, notified_index = -1;
    if (arrived) {
        notified_by = status.MPI_SOURCE;
        notified_index = msg;
    }

    // finder tells every other process
    MPI_Request *send_reqs = malloc(size * sizeof(MPI_Request));
    int num_sends = 0;
    if (found_at >= 0) {
        for (int r = 0; r < size; r++)
            if (r != rank)
                MPI_Isend(&found_at, 1, MPI_INT, r, FOUND_TAG, MPI_COMM_WORLD,
                          &send_reqs[num_sends++]);
    }

    // 50 can be found by 0, 1 or several processes. Count the finders so each
    // process knows how many messages are addressed to it.
    int i_sent = (found_at >= 0);
    int finders;
    MPI_Allreduce(&i_sent, &finders, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    int expected = finders - i_sent;

    if (expected == 0) {
        // nobody will ever send to us: cancel the pending receive
        MPI_Cancel(&recv_req);
        MPI_Wait(&recv_req, MPI_STATUS_IGNORE);
    } else {
        // the posted Irecv takes the first message, plain Recv the others
        if (!arrived)
            MPI_Wait(&recv_req, MPI_STATUS_IGNORE);
        for (int k = 1; k < expected; k++) {
            int extra;
            MPI_Recv(&extra, 1, MPI_INT, MPI_ANY_SOURCE, FOUND_TAG, MPI_COMM_WORLD,
                     MPI_STATUS_IGNORE);
        }
    }
    for (int k = 0; k < num_sends; k++)
        MPI_Wait(&send_reqs[k], MPI_STATUS_IGNORE);

    // collect a report from every process so rank 0 prints it in order
    int report[4] = {found_at, checked, notified_by, notified_index};
    int *all = NULL;
    if (rank == 0)
        all = malloc(4 * size * sizeof(int));
    MPI_Gather(report, 4, MPI_INT, all, 4, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        for (int r = 0; r < size; r++) {
            int *rep = &all[4 * r];
            if (rep[0] >= 0)
                printf("Process %d FOUND %d at index %d (element %d of its %d)\n",
                       r, TARGET, rep[0], rep[1], chunk);
            else if (rep[2] >= 0 && rep[1] < chunk)
                printf("Process %d stopped after checking %d of %d elements "
                       "(process %d found %d at index %d)\n",
                       r, rep[1], chunk, rep[2], TARGET, rep[3]);
            else
                printf("Process %d checked all %d elements, no %d in its part\n",
                       r, rep[1], TARGET);
        }
        if (finders == 0)
            printf("\n%d is not in the data\n", TARGET);
        else
            printf("\n%d was found by %d process(es)\n", TARGET, finders);
        free(all);
    }

    free(send_reqs);
    free(local);
    free(data);
    MPI_Finalize();
    return 0;
}
