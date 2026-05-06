import asyncio
import time

TOTAL_NUMBERS = 10**7
NUM_TASKS = 4


async def calculate_sum(start, end):
    partial_sum = sum(range(start, end))
    return partial_sum


async def main():
    tasks = []
    step = TOTAL_NUMBERS // NUM_TASKS

    start_time = time.time()

    for i in range(NUM_TASKS):
        start = i * step
        end = TOTAL_NUMBERS if i == NUM_TASKS - 1 else (i + 1) * step
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Total sum: {total_sum}")
    print(f"Execution time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
