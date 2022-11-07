from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tweet(Base):
    __tablename__ = "tweet"

    id = Column(String, primary_key=True, unique=True)
    full_text = Column(String)
    favorite_count = Column(Integer)
    retweet_count = Column(Integer)
    retweeted = Column(Boolean)
    lang = Column(String)
    created_at = Column(DateTime)
