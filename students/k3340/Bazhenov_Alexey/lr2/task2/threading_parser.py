import requests
import threading
import time

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


def parse_page(url):
    try:
        response = requests.get(url, timeout=5)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = (
            soup.title.string.strip()
            if soup.title
            else "No title"
        )

        save_to_db(url, title)

        print(f"{url} -> {title}")

    except Exception as e:
        print(f"Error parsing {url}: {e}")


def main():
    init_db()

    threads = []

    start_time = time.time()

    for url in urls:
        thread = threading.Thread(
            target=parse_page,
            args=(url,)
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()

    print(
        f"\nExecution time: "
        f"{end_time - start_time:.4f} seconds"
    )


if __name__ == "__main__":
    main()
