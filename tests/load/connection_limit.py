import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = ['https://dev.api.terafill.com/api/v1/client/timeout?timeout=1'] * 5
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            print(response)

if __name__ == '__main__':
    asyncio.run(main())
