import re
from typing import List

import bs4
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database import db

app = FastAPI(debug=True, title="Hackathon API")


class HackathonPost(BaseModel):
    title: str
    description: str
    date: str
    image_url: str
    link: str

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "date": self.date,
            "image_url": self.image_url,
            "link": self.link,
        }


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


@app.get("/hackathons", response_model=List[HackathonPost])
def current_hackathons():
    current_hackathons = parse_dou()
    new_hackathons = []
    for hackathon in current_hackathons:
        hackathon_found = db.hackathons.find_one({"title": hackathon.title})
        print(hackathon_found)
        if hackathon_found:
            continue

        db.hackathons.insert_one(hackathon.to_dict())
        new_hackathons.append(hackathon)

    if len(new_hackathons) == 0:
        return JSONResponse({"msg": "No new hackathons"}, 400)

    return JSONResponse(new_hackathons, 200)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
