import asyncio

async def fetch_value():
    await asyncio.sleep(1)
    return 42

async def main():
    result = await fetch_value()
    return result

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)