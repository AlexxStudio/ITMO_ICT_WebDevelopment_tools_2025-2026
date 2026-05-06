from multiprocessing import Process, Manager
import time

TOTAL_NUMBERS = 10**7
NUM_PROCESSES = 4


def calculate_sum(start, end, results, index):
    partial_sum = sum(range(start, end))
    results[index] = partial_sum


def main():
    processes = []

    manager = Manager()
    results = manager.list([0] * NUM_PROCESSES)

    step = TOTAL_NUMBERS // NUM_PROCESSES

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        start = i * step

        if i == NUM_PROCESSES - 1:
            end = TOTAL_NUMBERS
        else:
            end = (i + 1) * step

        process = Process(
            target=calculate_sum,
            args=(start, end, results, i)
        )

        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    total_sum = sum(results)

    end_time = time.time()

    print(f"Total sum: {total_sum}")
    print(f"Execution time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    main()
