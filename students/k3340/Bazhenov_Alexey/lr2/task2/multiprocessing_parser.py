import time
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup
from sqlmodel import Session

from students.k3340.Bazhenov_Alexey.lr1.connection import engine, init_db
from students.k3340.Bazhenov_Alexey.lr1.models import ParsedPage


urls = [
    "https://example.com",
    "https://python.org",
    "https://github.com",
    "https://stackoverflow.com"
]


def parse_and_save(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else "No title"

        with Session(engine) as session:
            parsed_page = ParsedPage(url=url, title=title)
            session.add(parsed_page)
            session.commit()

        return f"{url} -> {title}"

    except Exception as e:
        return f"Error parsing {url}: {e}"


def main():
    init_db()

    start_time = time.time()

    with Pool(processes=4) as pool:
        results = pool.map(parse_and_save, urls)

    for result in results:
        print(result)

    end_time = time.time()
    print(f"\nExecution time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    main()
