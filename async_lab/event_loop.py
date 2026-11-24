import asyncio
import time


async def task_a():
    print("A starts")
    await asyncio.sleep(2)
    print("A ends")


async def task_b():
    print("B starts")
    await asyncio.sleep(1)
    print("B ends")


async def main():
    a = asyncio.create_task(task_a())
    b = asyncio.create_task(task_b())

    await a
    await b


if __name__ == "__main__":
    start_time = time.perf_counter()
    asyncio.run(main())
    elapsed_time = time.perf_counter() - start_time

    print(f"Total elapsed time: {elapsed_time:.2f} seconds")