# Lab 7 – MPI for cluster computing

Each task is in its own folder:

| Folder | Files |
|---|---|
| `Task1/` | `task1_hello.c` |
| `Task2/` | `task2_send42.c` |
| `Task3/` | `task3_scatter.c` |
| `Task4/` | `task4a_telephone.c`, `task4b_bcast.c` |
| `Task5/` | `task5_search.c`, `data.txt` (+ test files `data_multi.txt`, `data_none.txt`) |
| `Task6/` | `task6a_send_recv.c`, `task6b_reduce.c` |
| `Task7/` | `task7_scatter_gather_sum.c` |
| `Task8/` | `task8_monte_carlo_pi.c` |

## How to compile and run

**Windows – MS-MPI + MinGW** (Option A of the setup guide, `libmsmpi.a` made with `gendef`/`dlltool`):

```bat
gcc Task1\task1_hello.c -o task1.exe -I"C:\Program Files (x86)\Microsoft SDKs\MPI\Include" -LC:\mpi -lmsmpi
mpiexec -n 4 task1.exe
```

**Open MPI / MPICH (macOS, Linux, WSL):**

```bash
mpicc Task1/task1_hello.c -o task1 && mpiexec -n 4 ./task1
mpicc Task2/task2_send42.c -o task2 && mpiexec -n 2 ./task2
mpicc Task3/task3_scatter.c -o task3 && mpiexec -n 4 ./task3
mpicc Task4/task4a_telephone.c -o task4a && mpiexec -n 4 ./task4a
mpicc Task4/task4b_bcast.c -o task4b && mpiexec -n 4 ./task4b
cd Task5 && mpicc task5_search.c -o task5 && mpiexec -n 4 ./task5 && cd ..
mpicc -O2 Task6/task6a_send_recv.c -o task6a -lm && mpiexec -n 4 ./task6a
mpicc -O2 Task6/task6b_reduce.c -o task6b -lm && mpiexec -n 4 ./task6b
mpicc Task7/task7_scatter_gather_sum.c -o task7 && mpiexec -n 4 ./task7
mpicc -O2 Task8/task8_monte_carlo_pi.c -o task8 -lm && mpiexec -n 4 ./task8
```

Task 5 reads `data.txt` from the current folder; another file can be given as an argument
(`mpiexec -n 4 ./task5 data_multi.txt`).

The outputs below come from MS-MPI 10.1 with MinGW gcc on Windows 11. Each process prints on its own, so
lines from different ranks can appear in any order. In Tasks 6–8 the per-process lines are listed by
rank here to make them easier to read.

---

## Task 1 – Greeting

`MPI_Init` starts MPI, `MPI_Comm_rank` / `MPI_Comm_size` give the process id and the number of processes,
and every process prints its own greeting.

```
> mpiexec -n 4 task1_hello.exe
Hello from process 0 of 4
Hello from process 1 of 4
Hello from process 2 of 4
Hello from process 3 of 4
```

## Task 2 – Passing 42 from process 0 to process 1

Rank 0 calls `MPI_Send(&number, 1, MPI_INT, 1, 0, ...)` and rank 1 calls
`MPI_Recv(&number, 1, MPI_INT, 0, 0, ...)`. The tag (0) and the communicator are the same on both sides.
The program stops with a message if it is not started with exactly 2 processes.

```
> mpiexec -n 2 task2_send42.exe
Process 0 sent number 42 to process 1
Process 1 received number 42 from process 0
```

## Task 3 – Scatter

Rank 0 holds `data[4] = {10, 20, 30, 40}`. `MPI_Scatter(data, 1, MPI_INT, &element, 1, MPI_INT, 0, ...)`
gives one element to each of the 4 processes, including rank 0 itself.

```
> mpiexec -n 4 task3_scatter.exe
Process 1 received element 20
Process 2 received element 30
Process 0 scatters {10, 20, 30, 40}
Process 0 received element 10
Process 3 received element 40
```

## Task 4 – Telephone game

**(a) `task4a_telephone.c`** – Rank 0 picks the number 7 and sends it to rank 1. Every other rank first
calls `MPI_Recv` from `rank - 1` and only then calls `MPI_Send` to `rank + 1`. The last rank only receives.
The order matters: a rank cannot pass on a number it has not received yet. `MPI_Recv` blocks until the
number arrives, so the value moves 0 → 1 → 2 → 3 in that order.

```
> mpiexec -n 4 task4a_telephone.exe
Process 1 received 7 from process 0
Process 0 starts the game with number 7
Process 2 received 7 from process 1
Process 3 received 7 from process 2
```

(The "received" lines happen in rank order. The line from process 0 can still be printed later, because
each process writes to the console on its own.)

**(b) `task4b_bcast.c`** – The whole send/receive chain is replaced by one collective call,
`MPI_Bcast(&number, 1, MPI_INT, 0, MPI_COMM_WORLD)`. Every rank calls it, and rank 0 is the root.

```
> mpiexec -n 4 task4b_bcast.exe
Process 1 received 7
Process 0 starts the game with number 7
Process 3 received 7
Process 2 received 7
```

## Task 5 – Array search with a non-blocking receive

`data.txt` has 40 whole numbers (10 per process with 4 processes). There is one 50, at index 23, which is
element 4 of rank 2's part:

```
19 89 40 3 89 43 12 39 87 92
61 27 26 22 21 62 7 42 30 54
89 59 13 50 20 73 61 92 93 30
23 53 72 1 97 12 61 39 74 82
```

How it works:

1. **Master** (rank 0) reads `data.txt`, then broadcasts the count. If the count does not divide evenly
   by the number of processes, every process stops cleanly.
2. `MPI_Scatter` sends `n / size` numbers to each process (the master searches its own part too).
3. Each process posts `MPI_Irecv(..., MPI_ANY_SOURCE, FOUND_TAG, ...)` **before** it starts searching.
4. The search checks one element at a time, with `Sleep(100)` (Windows) or `usleep(100000)` per element.
   After each element, `MPI_Test` checks the pending receive, and the process stops as soon as the message
   has arrived. A process that finds 50 sends its global index to every other process with `MPI_Isend`.
5. **Ending correctly whether 50 appears once, several times, or not at all:**
   - `MPI_Allreduce` adds up how many processes found 50. Each process now knows how many messages are
     addressed to it: `finders - (1 if it found 50 itself)`.
   - If that number is 0, nobody will ever match the `MPI_Irecv`, so it is cancelled with
     `MPI_Cancel` + `MPI_Wait`.
   - Otherwise, the `MPI_Irecv` gets the first message (`MPI_Wait` if it has not arrived yet), and plain
     `MPI_Recv` calls get the rest. So every message that was sent is received.
   - Each sender waits for its `MPI_Isend` requests before `MPI_Finalize`.
6. `MPI_Gather` collects a small report from each process, so rank 0 prints the results in rank order.

```
> mpiexec -n 4 task5_search.exe
Master read 40 numbers from data.txt, 10 per process

Process 0 stopped after checking 5 of 10 elements (process 2 found 50 at index 23)
Process 1 stopped after checking 6 of 10 elements (process 2 found 50 at index 23)
Process 2 FOUND 50 at index 23 (element 4 of its 10)
Process 3 stopped after checking 5 of 10 elements (process 2 found 50 at index 23)

50 was found by 1 process(es)
```

Process 2 finds 50 at its 4th element (about 400 ms). The other processes get the message during their
4th–5th element and stop, so they never search the rest of their part. The exact element where a process
stops can change by one or two between runs, because of timing and process scheduling.

The other two cases also finish correctly:

```
> mpiexec -n 4 task5_search.exe data_multi.txt      (50 at index 14 and index 34)
Process 0 stopped after checking 6 of 10 elements (process 3 found 50 at index 34)
Process 1 FOUND 50 at index 14 (element 5 of its 10)
Process 2 stopped after checking 6 of 10 elements (process 1 found 50 at index 14)
Process 3 FOUND 50 at index 34 (element 5 of its 10)

50 was found by 2 process(es)

> mpiexec -n 4 task5_search.exe data_none.txt       (no 50)
Process 0 checked all 10 elements, no 50 in its part
Process 1 checked all 10 elements, no 50 in its part
Process 2 checked all 10 elements, no 50 in its part
Process 3 checked all 10 elements, no 50 in its part

50 is not in the data

> mpiexec -n 3 task5_search.exe
data.txt has 40 numbers, which is not a multiple of 3 processes
```

## Task 6 – Counting primes between 2 and 10,000,000

The range is split into equal blocks, one per process (the last block also takes any leftover numbers).
Each process counts the primes in its block with trial division up to √n.

- **(a) `task6a_send_recv.c`** – ranks 1–3 `MPI_Send` their counts to rank 0. Rank 0 calls `MPI_Recv` once
  for each of them and adds the counts to its own.
- **(b) `task6b_reduce.c`** – the send/receive loop is replaced by
  `MPI_Reduce(&local, &count, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD)`.

Both print the correct total, **664579**:

```
> mpiexec -n 4 task6a_send_recv.exe
Process 0: [2, 2500000] has 183072 primes
Process 1: [2500001, 4999999] has 165441 primes
Process 2: [5000000, 7499998] has 159748 primes
Process 3: [7499999, 10000000] has 156318 primes

Number of primes between 2 and 10000000: 664579
Time: 0.511 s

> mpiexec -n 4 task6b_reduce.exe
Process 0: [2, 2500000] has 183072 primes
Process 1: [2500001, 4999999] has 165441 primes
Process 2: [5000000, 7499998] has 159748 primes
Process 3: [7499999, 10000000] has 156318 primes

Number of primes between 2 and 10000000: 664579
Time: 0.508 s
```

Both versions take the same time, because the program spends almost all of it counting primes. The
reduce version is shorter and lets MPI choose how to combine the values (for example, in a tree).

## Task 7 – Scatter, partial sums, gather

1. Rank 0 makes an array of `5 × size` random numbers (1–100).
2. `MPI_Scatter` gives 5 numbers to each process.
3. Each process adds up its 5 numbers.
4. `MPI_Gather` collects the partial sums on rank 0, which adds them up. The result is checked against a
   normal serial sum.

```
> mpiexec -n 4 task7_scatter_gather_sum.exe
Root generated 20 numbers: 91 46 49 58 14 75 73 94 8 38 20 40 85 22 58 96 72 2 72 59

Process 0 got {91, 46, 49, 58, 14}, local sum = 258
Process 1 got {75, 73, 94, 8, 38}, local sum = 288
Process 2 got {20, 40, 85, 22, 58}, local sum = 225
Process 3 got {96, 72, 2, 72, 59}, local sum = 301

Root gathered partial sums: 258 288 225 301
Final sum = 1072
Serial check = 1072 (match)
```

## Task 8 – Monte-Carlo estimate of PI

Random points (x, y) are picked in the unit square. The fraction that falls inside the quarter circle
x² + y² ≤ 1 is close to π/4, so π ≈ 4 · hits / points.

100,000,000 points are split evenly over the processes. Each process uses its own xorshift random
generator, seeded with the time and its rank, so the processes produce different points. Windows' `rand()`
only gives 15-bit numbers, which is why it is not used here. `MPI_Reduce` with `MPI_SUM` (type
`MPI_LONG_LONG`) adds up the hits on rank 0.

```
> mpiexec -n 4 task8_monte_carlo_pi.exe
Process 0: 19633022 of 25000000 points inside the circle
Process 1: 19635994 of 25000000 points inside the circle
Process 2: 19632997 of 25000000 points inside the circle
Process 3: 19632916 of 25000000 points inside the circle

Points: 100000000, inside: 78534929
Estimated PI = 3.14139716
Error        = 0.00019549
Time: 0.098 s
```

The error shrinks roughly like 1/√N. With 10⁸ points, the expected error is about 0.00016.
