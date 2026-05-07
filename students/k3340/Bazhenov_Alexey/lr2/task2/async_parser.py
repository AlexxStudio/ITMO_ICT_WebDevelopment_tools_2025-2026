import asyncio
import time

import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import Session

from students.k3340.Bazhenov_Alexey.lr1.connection import (
    engine,
    init_db
)

from students.k3340.Bazhenov_Alexey.lr1.models import (
    ParsedPage
)


urls = [
    "https://example.com",
    "https://python.org",
    "https://github.com",
    "https://stackoverflow.com"
]


def save_to_db(url, title):
    with Session(engine) as session:
        parsed_page = ParsedPage(
            url=url,
            title=title
        )

        session.add(parsed_page)
        session.commit()


async def parse_page(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            html = await response.text()

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            title = (
                soup.title.string.strip()
                if soup.title
                else "No title"
            )

            save_to_db(url, title)

            return f"{url} -> {title}"

    except Exception as e:
        return f"Error parsing {url}: {e}"


async def main():
    init_db()

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [
            parse_page(session, url)
            for url in urls
        ]

        results = await asyncio.gather(*tasks)

    for result in results:
        print(result)

    end_time = time.time()

    print(
        f"\nExecution time: "
        f"{end_time - start_time:.4f} seconds"
    )


if __name__ == "__main__":
    asyncio.run(main())
