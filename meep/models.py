from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Account(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "account"

    username = Column(String, primary_key=True, unique=True)
    email = Column(String)


class Tweet(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "tweet"

    id = Column(String, primary_key=True, unique=True)
    account_id = Column(String, ForeignKey("account.username"), nullable=False)
    full_text = Column(String)
    favorite_count = Column(Integer)
    retweet_count = Column(Integer)
    retweeted = Column(Boolean)
    lang = Column(String)
    created_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"{self.id}, {self.created_at} - {self.full_text}"

    @property
    def link(self) -> str:
        return f"https://twitter.com/{self.account_id}/status/{self.id}"
