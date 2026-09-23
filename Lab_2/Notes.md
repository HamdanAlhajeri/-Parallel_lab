# Lab 2 and Lab 3

Run `python Lab_2/Lab2.py` from the repository folder. All seven tasks and five post-lab exercises run in order. The existing Task 1 is preserved.

Task 3 also includes the literal 1,000-process experiment. Run `python Lab_2/Lab2.py --1000-processes` to include it. That experiment may exhaust system resources; the default run uses the pool version. A process wrapper prints each cube because a Process target's return value is not automatically delivered to the parent.

## Comments on the results

- Task 1: Names such as p1, p2 and p3 make the output easier to identify. Anonymous processes receive automatic names. Output order can vary.
- Task 2: A shared lock keeps each worker's two print calls together. Without a lock, output may interleave, although a particular run can still look orderly. Worker count is CPU count minus one, with a minimum of one on a single-core machine.
- Task 3: Python can create more processes than CPU cores, contrary to the parenthetical claim in the handout. The OS schedules them. Whether 1,000 processes succeed depends on memory and other system limits. A pool reuses a bounded set of workers for the 1,000 inputs.
- Task 5: The child processes calculate their respective sums and send the results to the parent. The expected sums are 500500 and -500500.
- Task 6: Both versions add the same million integers. Data generation is outside the timers. Parallel timing includes starting processes, sending inputs, receiving results and joining. Process overhead can make this short calculation slower in parallel. Speedup is sequential time divided by parallel time; values below one indicate a slowdown.
- Task 7: Pi is estimated as four times the fraction of points inside the unit circle. Both versions use identical seeded batches so their estimates match, while differing from math.pi due to sampling error. Pool creation and shutdown are included in parallel timing.
- Post-lab 1: Each version performs two countdowns from ten million to zero, keeping total work equal. Startup and coordination costs can outweigh the benefit of using two cores. Actual timings are machine dependent.
- Post-lab 2: Pool tasks use p1, p2 and p3 as temporary worker names. A pool can reuse a process for multiple tasks, so three calls do not guarantee three distinct PIDs.
- Post-lab 3: Each worker pauses 0.5 seconds between its start and completion messages. Workers run concurrently.
- Post-lab 4: Python range(2, 100) includes 2 through 99.
- Post-lab 5: Pool workers sort contiguous chunks using merge sort. The parent merges the sorted chunks to obtain the final sorted list.

`results.txt` contains output from the default verification run. The optional 1,000-process experiment was not run. For the screenshots requested by the handout, capture the relevant functions and their console output in your IDE.
