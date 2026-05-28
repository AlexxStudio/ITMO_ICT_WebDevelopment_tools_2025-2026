import aiohttp
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Parser Service")


class ParseRequest(BaseModel):
    url: str


@app.get("/")
async def root():
    return {"message": "Parser service is working"}


@app.post("/parse")
async def parse_page(data: ParseRequest):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(data.url, timeout=10) as response:
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "No title"

        return {
            "url": data.url,
            "title": title
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
