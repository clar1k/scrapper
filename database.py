from os import environ as env

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv(".evn.prod")

connection = MongoClient(env.get("MONGO_URI"), server_api=ServerApi("1"))
db = connection["hackathons"]
