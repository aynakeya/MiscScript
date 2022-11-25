import json
import traceback

import requests
import sqlalchemy
from sqlalchemy import Column, Integer, String, Text

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

engine = sqlalchemy.create_engine("sqlite:///nga.db")
Base = declarative_base()
session:Session = sessionmaker(bind=engine)()


class Post(Base):
    __tablename__ = "nga_post"

    id = Column(Integer,primary_key=True,autoincrement=True)
    tid = Column(Integer)
    page = Column(Integer)
    data = Column(Text)

Base.metadata.create_all(engine)

