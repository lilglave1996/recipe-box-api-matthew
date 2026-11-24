
import asyncio
import time


async def task_a():
    print("A starts")
    await asyncio.sleep(3)
    print("A ends")
    return "Result A"


async def task_b():
    print("B starts")
    await asyncio.sleep(1)
    print("B ends")
    return "Result B"


async def task_c():
    print("C starts")
    await asyncio.sleep(2)
    print("C ends")
    return "Result C"


async def main():
    start = time.perf_counter()

    results = await asyncio.gather(
        task_a(),
        task_b(),
        task_c()
    )

    elapsed = time.perf_counter() - start

    print("Results:", results)
    print(f"Total elapsed time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
