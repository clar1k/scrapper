from pprint import pprint
from fastapi import FastAPI
import bs4
import requests
from icecream import ic
from pydantic import BaseModel
import re
import uvicorn
from database import db


app = FastAPI(debug=True, title="Hackathon API")


class HackathonPost(BaseModel):
    title: str
    description: str
    date: str
    image_url: str
    link: str


def parse_dou() -> list[HackathonPost] or None:
    URL = "https://dou.ua/calendar/tags/%D1%85%D0%B0%D0%BA%D0%B0%D1%82%D0%BE%D0%BD/"

    fake_user_agent = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    response = requests.get(URL, headers=fake_user_agent)
    CONTENT = response.content

    soup = bs4.BeautifulSoup(CONTENT, "html.parser", from_encoding="utf-8")

    post_cards = soup.find_all("article", attrs={"class": "b-postcard"})

    hackathon_posts = []
    for post in post_cards:
        text = post.find("a")
        url = text.attrs["href"]

        header_text: str = text.text
        header_text = header_text.replace("\t", "")
        cleaned_text = re.sub(r"\s+", " ", header_text.strip())

        description = post.find("p", attrs={"class": "b-typo"})
        description: str = description.text
        description = description.replace("\t", "")
        description = re.sub(r"\s+", " ", description.strip())

        image_url = post.find("img")
        image_url = image_url.attrs["srcset"]
        image_url = image_url[0 : image_url.find(".png") + 4]

        date = post.find("span", attrs={"class": "date"})
        date = date.text

        hackathon_post = HackathonPost(
            title=cleaned_text,
            description=description,
            date=date,
            image_url=image_url,
            link=url,
        )
        hackathon_posts.append(hackathon_post)
    return hackathon_posts


@app.get("/hackathons", response_model=list[HackathonPost])
def current_hackathons():
    hackathons = parse_dou()
    for hackathon in hackathons:
        ic(hackathon)
    return hackathons


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
