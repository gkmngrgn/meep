from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel


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
    in_reply_to_status_id: Optional[int] = None
    self_reply_count: int = 0

    @classmethod
    def from_row(cls, row: tuple[object, ...]) -> Tweet:
        return cls(
            id=row[0],
            account_id=row[1],
            full_text=row[2],
            favorite_count=row[3],
            retweet_count=row[4],
            retweeted=row[5],
            lang=row[6],
            created_at=row[7],
            in_reply_to_status_id=row[8] if len(row) > 8 else None,
            self_reply_count=row[9] if len(row) > 9 else 0,
        )

    def to_row(
        self,
    ) -> tuple[int, str, str, int, int, bool, str, datetime.datetime, Optional[int]]:
        return (
            self.id,
            self.account_id,
            self.full_text,
            self.favorite_count,
            self.retweet_count,
            self.retweeted,
            self.lang,
            self.created_at,
            self.in_reply_to_status_id,
        )

    @property
    def link(self) -> str:
        return f"https://twitter.com/{self.account_id}/status/{self.id}"
