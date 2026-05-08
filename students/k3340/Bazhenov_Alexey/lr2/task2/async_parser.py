import asyncio
import time

import aiohttp
from bs4 import BeautifulSoup
from sqlmodel.ext.asyncio.session import AsyncSession

from students.k3340.Bazhenov_Alexey.lr1.models import ParsedPage
from students.k3340.Bazhenov_Alexey.lr2.task2.async_connection import (
    async_engine,
    init_async_db
)


urls = [
    "https://example.com",
    "https://python.org",
    "https://github.com",
    "https://stackoverflow.com"
]


async def parse_and_save(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            title = soup.title.string.strip() if soup.title else "No title"

            async with AsyncSession(async_engine) as db_session:
                parsed_page = ParsedPage(url=url, title=title)
                db_session.add(parsed_page)
                await db_session.commit()

            print(f"{url} -> {title}")

    except Exception as e:
        print(f"Error parsing {url}: {e}")


async def main():
    await init_async_db()

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"\nExecution time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
