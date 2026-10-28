# Lab 6 – Multithreading and OpenMP

Each task is in its own folder:

| Folder | Files |
|---|---|
| `Task1/` | `program1.c`, `program2.c` |
| `Task2/` | `task2.c` |
| `Task3/` | `task3a_sequential.c`, `task3b_pthreads.c` |
| `Task4/` | `task4a_sequential.c`, `task4b_pthreads.c`, `task4c_no_race.c` |

## How to compile and run (Linux / WSL)

Compile with `-O0` so the compiler does not optimise the race in Task 1 / 4b away.

```bash
gcc -O0 -pthread Task1/program1.c -o p1 && ./p1
gcc -O0 -pthread Task1/program2.c -o p2 && ./p2
gcc -O0 -pthread Task2/task2.c -o t2 && ./t2
gcc -O0 Task3/task3a_sequential.c -o t3a -lm && ./t3a
gcc -O0 -pthread Task3/task3b_pthreads.c -o t3b -lm && ./t3b
gcc -O0 Task4/task4a_sequential.c -o t4a && ./t4a
gcc -O0 -pthread Task4/task4b_pthreads.c -o t4b && ./t4b
gcc -O0 -pthread Task4/task4c_no_race.c -o t4c && ./t4c
```

---

## Task 1

**Program 1** prints a number that is usually **less than 500000** and changes from run to run
(three test runs gave 138218, 122631, 135883).

All 5 threads are created first and run at the same time. `counter++` is not one instruction – it is
*load counter → add 1 → store counter*. If two threads load the same value, both add 1 and both
store it back, one of the increments is lost. This is a **data race** on the shared variable
`counter`, so the final result is unpredictable and smaller than 5 × 100000.

**Program 2** always prints **500000**.

Here `pthread_join` is called right after each `pthread_create`, so main waits for each thread to
finish before starting the next one. Only one thread touches `counter` at any time, so there is no
race – but there is also no parallelism; the threads run one after another, like a sequential loop.

## Task 2

`main` creates a thread that runs `func1()`, runs `func2()` itself, then waits with `pthread_join`.
A mutex `lock` protects the shared variables `x`, `y` and the `printf` in both functions, so each
function's update+print happens as one block.

**Possible outputs (with the lock)** – only the order of the two blocks can change:

1. `func1` gets the lock first:
   ```
   Hello from func1: x,y,z is 0,1,5.
   Hello from func2: y is 1, z is 7.
   ```
2. `func2` gets the lock first:
   ```
   Hello from func2: y is 0, z is 7.
   Hello from func1: x,y,z is 2,1,5.
   ```

`z` is always 5 in `func1` and 7 in `func2` because `z` is a local variable (each thread has its own
stack). Without the lock, mixed results are also possible, e.g. `func2` prints `y is 1` while
`func1` prints `x = 0`, or both print `x = 0` / `y = 0`, depending on how the threads interleave.

## Task 3

- **(a)** `task3a_sequential.c` – loops over 0..100000 and calls `isPrime(n)`, which tries every
  divisor from 2 to √n.
- **(b)** `task3b_pthreads.c` – splits 0..100000 into 4 ranges. Each range's endpoints are stored in a
  `struct Range {start, end}` and a pointer to it is passed to `pthread_create`. Each thread counts
  primes in a local variable and then adds it to the shared `pcount` inside
  `pthread_mutex_lock / unlock`, so there is no race on `pcount`.

Both programs print **9592** primes between 0 and 100000.

## Task 4

- **(a)** `task4a_sequential.c` – standard Sieve of Eratosthenes up to N = 2,000,000.
  Result: **148933** primes.
- **(b)** `task4b_pthreads.c` – two threads, `t1` for [0, 1,000,000] and `t2` for
  [1,000,001, 2,000,000]; endpoints passed in a struct. This version has race conditions:
  - both threads do `count++` on the same global variable with no lock, so updates can be lost and
    the total can come out wrong (test runs gave 140777, 140562, 141549, 144496 instead of 148933);
  - `t2` finds its sieving primes by reading `is_composite[2..1414]`, which `t1` is writing at the
    same time.
- **(c)** `task4c_no_race.c` – race-free version. Always prints **148933**
  (t1: 78498, t2: 70435).

**Methodology used in (c):**

1. **Remove the shared reads.** The primes up to √N (≈1414) are computed sequentially in `main`
   *before* the threads start and stored in `base_primes[]`. After that the array is only read,
   never written, so the threads can share it safely (immutable data).
2. **Partition the writes.** Each thread only marks cells inside its own range
   (`first multiple of p ≥ start` up to `end`), so the two threads never write the same element of
   `is_composite`.
3. **Private counters + mutex.** Each thread counts primes in a local variable and then adds it to
   the global `count` once, inside `pthread_mutex_lock / pthread_mutex_unlock`. The critical section
   is a single addition per thread, so the lock costs almost nothing.
