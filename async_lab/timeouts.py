import asyncio
import httpx
import time

from config import Config

BASE_URL = Config.SLOW_SERVICE_BASE_URL

ingredients = ["eggs", "tomatoes", "peppers"]


async def main():
    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        requests = [
            asyncio.wait_for(
                client.get(f"{BASE_URL}/nutrition/{ingredient}"),
                timeout=0.5
            )
            for ingredient in ingredients
        ]

        async def collect_result(request):
            try:
                return await request, None
            except asyncio.TimeoutError:
                return None, "timeout"
            except httpx.ConnectError:
                return None, "connection error"

        responses = await asyncio.gather(
            *(collect_result(request) for request in requests)
        )

        for ingredient, (response, error) in zip(ingredients, responses):
            if response is None:
                print(f"{ingredient}: MISSING ({error})")
            else:
                print(f"{ingredient}: {response.status_code}")

    elapsed_time = time.perf_counter() - start_time
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
