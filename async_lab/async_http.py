import asyncio
import httpx
import time

BASE_URL = "http://127.0.0.1:5001"

ingredients = ["eggs", "tomatoes", "peppers"]


async def main():
    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        requests = [
            client.get(f"{BASE_URL}/nutrition/{ingredient}")
            for ingredient in ingredients
        ]

        responses = await asyncio.gather(*requests)

        for ingredient, response in zip(ingredients, responses):
            print(f"{ingredient}: {response.status_code}")

    elapsed_time = time.perf_counter() - start_time
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())