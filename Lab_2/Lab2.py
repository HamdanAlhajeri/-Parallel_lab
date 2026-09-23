import os 
import math
import random
import time
import sys
import multiprocessing as mp

def print_hello():
    process = mp.current_process()

    print(f"hello from child process")
    print(f"Process name: {process.name}")
    print(f"Child PID: {os.getpid()}")
    print(f"Parent PID: {os.getppid()}")

def task1():
    print("____________Named Proceses____________")
    processes = [mp.Process(target=print_hello, name="p1"),
                 mp.Process(target=print_hello, name="p2"),
                 mp.Process(target=print_hello, name="p3")]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print("____________Anonymous Processes____________")

    processes = [mp.Process(target=print_hello),
                 mp.Process(target=print_hello),
                 mp.Process(target=print_hello)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

def my_id(lock=None):
    process = mp.current_process()

    if lock is not None:
        lock.acquire()

    try:
        print(f"Station: Dockyard")
        print(f"Hi, I'm worker {process.name} (with PID {os.getpid()})")
    finally:
        if lock is not None:
            lock.release()


def task2():
    workers = mp.cpu_count() - 1
    if workers < 1:
        workers = 1
    print(f"CPU cores: {mp.cpu_count()}")

    for use_lock in [True, False]:
        if use_lock:
            print("____________With Lock____________")
            lock = mp.Lock()
        else:
            print("____________Without Lock____________")
            lock = None

        processes = []
        for i in range(workers):
            if i < 26:
                name = chr(97 + i)
            else:
                name = f"worker{i + 1}"
            processes.append(mp.Process(target=my_id, args=(lock,), name=name))

        for p in processes:
            p.start()

        for p in processes:
            p.join()


def cube(x):
    return x ** 3


def print_cube(x):
    print(f"{x} cubed: {cube(x)}")


def task3(run_processes=False):
    if run_processes:
        print("____________1000 Processes____________")
        processes = []
        for i in range(1, 1001):
            processes.append(mp.Process(target=print_cube, args=(i,)))

        started = []
        try:
            for p in processes:
                p.start()
                started.append(p)
        finally:
            for p in started:
                p.join()
    else:
        print("Use --1000-processes to run the 1000-process experiment.")

    print("____________Cube Pool____________")
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(cube, range(1, 1001))

    print(results)


def greet(queue):
    for i in range(5):
        name = queue.get()
        print(f"Hello {name}", flush=True)


def sendName():
    queue = mp.Queue()
    p = mp.Process(target=greet, args=(queue,))
    p.start()

    names = ["Ali", "Omar", "Sara", "Ahmed", "Noor"]
    for i in range(len(names)):
        queue.put(names[i])
        if i < len(names) - 1:
            time.sleep(1)

    p.join()
    queue.close()
    queue.join_thread()


def task4():
    print("____________Queue Greetings____________")
    sendName()


def addPositive(queue):
    total = 0
    for i in range(1, 1001):
        total += i
    queue.put(("Positive sum", total))


def addNegative(queue):
    total = 0
    for i in range(-1000, 0):
        total += i
    queue.put(("Negative sum", total))


def task5():
    print("____________Positive and Negative Sums____________")
    queue = mp.Queue()
    processes = [mp.Process(target=addPositive, args=(queue,)),
                 mp.Process(target=addNegative, args=(queue,))]

    for p in processes:
        p.start()

    for i in range(2):
        name, total = queue.get()
        print(f"{name}: {total}")

    for p in processes:
        p.join()

    queue.close()
    queue.join_thread()


def add_numbers(numbers, queue=None):
    total = 0
    for number in numbers:
        total += number

    if queue is not None:
        queue.put(total)
    return total


def task6():
    print("____________Sequential and Parallel Addition____________")
    numbers = []
    for i in range(1000000):
        numbers.append(random.randint(1, 100))

    start = time.perf_counter()
    sequential_result = add_numbers(numbers)
    sequential_time = time.perf_counter() - start

    queue = mp.Queue()
    processes = [mp.Process(target=add_numbers, args=(numbers[:500000], queue)),
                 mp.Process(target=add_numbers, args=(numbers[500000:], queue))]

    start = time.perf_counter()
    for p in processes:
        p.start()

    parallel_result = queue.get() + queue.get()
    for p in processes:
        p.join()
    parallel_time = time.perf_counter() - start

    print(f"Sequential sum: {sequential_result}")
    print(f"Parallel sum: {parallel_result}")
    print(f"Sequential time: {sequential_time:.6f} seconds")
    print(f"Parallel time: {parallel_time:.6f} seconds")
    print(f"Speedup: {sequential_time / parallel_time:.4f}")
    queue.close()
    queue.join_thread()


def points_in_circle(args):
    trials, seed = args
    generator = random.Random(seed)
    inside = 0

    for i in range(trials):
        x = generator.uniform(-1, 1)
        y = generator.uniform(-1, 1)
        distance = math.sqrt(x ** 2 + y ** 2)
        if distance <= 1:
            inside += 1

    return inside


def task7():
    print("____________Monte Carlo Pi____________")
    trials = 1000000
    workers = mp.cpu_count()
    tasks = []
    for i in range(workers):
        count = trials // workers
        if i < trials % workers:
            count += 1
        tasks.append((count, i))

    start = time.perf_counter()
    sequential_result = 0
    for task in tasks:
        sequential_result += points_in_circle(task)
    sequential_time = time.perf_counter() - start

    start = time.perf_counter()
    with mp.Pool(workers) as pool:
        results = pool.map(points_in_circle, tasks)

    parallel_result = 0
    for result in results:
        parallel_result += result
    parallel_time = time.perf_counter() - start

    print(f"Sequential pi: {4 * sequential_result / trials}")
    print(f"Parallel pi: {4 * parallel_result / trials}")
    print(f"Actual pi: {math.pi}")
    print(f"Sequential time: {sequential_time:.6f} seconds")
    print(f"Parallel time: {parallel_time:.6f} seconds")
    print(f"Speedup: {sequential_time / parallel_time:.4f}")


def cpu_bound(n=10000000):
    while n > 0:
        n -= 1


def post_task1():
    print("____________CPU Bound____________")
    start = time.perf_counter()
    for i in range(2):
        cpu_bound()
    sequential_time = time.perf_counter() - start

    processes = [mp.Process(target=cpu_bound),
                 mp.Process(target=cpu_bound)]
    start = time.perf_counter()
    for p in processes:
        p.start()

    for p in processes:
        p.join()
    process_time = time.perf_counter() - start

    start = time.perf_counter()
    with mp.Pool(2) as pool:
        pool.map(cpu_bound, [10000000, 10000000])
    pool_time = time.perf_counter() - start

    print(f"Sequential time: {sequential_time:.6f} seconds")
    print(f"Process time: {process_time:.6f} seconds")
    print(f"Pool time: {pool_time:.6f} seconds")
    print(f"Process speedup: {sequential_time / process_time:.4f}")
    print(f"Pool speedup: {sequential_time / pool_time:.4f}")


def pool_hello(name):
    process = mp.current_process()
    old_name = process.name
    if name is not None:
        process.name = name
    print_hello()
    process.name = old_name


def post_task2():
    print("____________Named Pool Tasks____________")
    with mp.Pool(3) as pool:
        pool.map(pool_hello, ["p1", "p2", "p3"])

    print("____________Anonymous Pool Tasks____________")
    with mp.Pool(3) as pool:
        pool.map(pool_hello, [None, None, None])


def dig(hole):
    process = mp.current_process()
    print(f"Worker {process.name} is digging hole {hole}", flush=True)
    time.sleep(0.5)
    print(f"Worker {process.name} finished hole {hole}", flush=True)


def assignDiggers():
    processes = []
    for i in range(10):
        processes.append(mp.Process(target=dig, args=(i,), name=chr(65 + i)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()


def post_task3():
    print("____________Hole Diggers____________")
    assignDiggers()


def sqr(x):
    return x ** 2


def post_task4():
    print("____________Squares____________")
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(sqr, range(2, 100))

    print(results)


def merge(left, right):
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    while i < len(left):
        result.append(left[i])
        i += 1

    while j < len(right):
        result.append(right[j])
        j += 1
    return result


def merge_sort(numbers):
    if len(numbers) <= 1:
        return numbers

    middle = len(numbers) // 2
    left = merge_sort(numbers[:middle])
    right = merge_sort(numbers[middle:])
    return merge(left, right)


def post_task5():
    print("____________Parallel Merge Sort____________")
    numbers = []
    for i in range(100):
        numbers.append(random.randint(1, 1000))
    workers = min(mp.cpu_count(), len(numbers))
    size = math.ceil(len(numbers) / workers)
    parts = []
    for i in range(0, len(numbers), size):
        part = []
        for j in range(i, min(i + size, len(numbers))):
            part.append(numbers[j])
        parts.append(part)

    with mp.Pool(workers) as pool:
        parts = pool.map(merge_sort, parts)

    while len(parts) > 1:
        merged = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                merged.append(merge(parts[i], parts[i + 1]))
            else:
                merged.append(parts[i])
        parts = merged

    print(f"Original list: {numbers}")
    print(f"Sorted list: {parts[0]}")


if __name__ == "__main__":
    task1()
    task2()
    task3("--1000-processes" in sys.argv)
    task4()
    task5()
    task6()
    task7()
    post_task1()
    post_task2()
    post_task3()
    post_task4()
    post_task5()
