import threading
import time

TOTAL_NUMBERS = 10**7
NUM_THREADS = 4


def calculate_sum(start, end, results, index):
    partial_sum = sum(range(start, end))
    results[index] = partial_sum


def main():
    threads = []
    results = [0] * NUM_THREADS

    step = TOTAL_NUMBERS // NUM_THREADS

    start_time = time.time()

    for i in range(NUM_THREADS):
        start = i * step

        if i == NUM_THREADS - 1:
            end = TOTAL_NUMBERS
        else:
            end = (i + 1) * step

        thread = threading.Thread(
            target=calculate_sum,
            args=(start, end, results, i)
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)

    end_time = time.time()

    print(f"Total sum: {total_sum}")
    print(f"Execution time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    main()
