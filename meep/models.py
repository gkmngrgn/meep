from __future__ import annotations
from pydantic import BaseModel

import datetime


class Account(BaseModel):
    username: str
    email: str

    @classmethod
    def from_row(cls, row) -> Account:
        return cls(username=row[0], email=row[1])

    def to_row(self) -> tuple[str, str]:
        return self.username, self.email


class Tweet(BaseModel):
    id: int
    account_id: str
    full_text: str
    favorite_count: int
    retweet_count: int
    retweeted: bool
    lang: str
    created_at: datetime.datetime

    @classmethod
    def from_row(cls, row) -> Tweet:
        return cls(
            id=row[0],
            account_id=row[1],
            full_text=row[2],
            favorite_count=row[3],
            retweet_count=row[4],
            retweeted=row[5],
            lang=row[6],
            created_at=row[7],
        )

    def to_row(self) -> tuple[int, int, str, int, int, bool, str, str]:
        return (
            self.id,
            self.account_id,
            self.full_text,
            self.favorite_count,
            self.retweet_count,
            self.retweeted,
            self.lang,
            self.created_at,
        )

    @property
    def link(self) -> str:
        return f"https://twitter.com/{self.account_id}/status/{self.id}"
