import requests
from sqlmodel import Session

from app.celery_app import celery
from app.connection import engine
from app.models import ParsedPage


@celery.task
def parse_url_task(url: str):
    response = requests.post(
        "http://parser:8001/parse",
        json={"url": url},
        timeout=10
    )
    response.raise_for_status()

    parsed_data = response.json()

    with Session(engine) as session:
        parsed_page = ParsedPage(
            url=parsed_data["url"],
            title=parsed_data["title"]
        )

        session.add(parsed_page)
        session.commit()
        session.refresh(parsed_page)

        return {
            "id": parsed_page.id,
            "url": parsed_page.url,
            "title": parsed_page.title
        }
