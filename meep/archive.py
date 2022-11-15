import json
from typing import Any, Dict, List

from dateutil.parser import parse as parse_date

from meep.models import Account, Tweet


def __jsonize(content: bytes) -> List[Dict[str, Any]]:
    start_index = content.index(b"[")
    end_index = content.rindex(b"]") + 1
    data: List[Dict[str, Any]] = json.loads(content[start_index:end_index])
    return data


def parse_account_data(content: bytes) -> List[Account]:
    return [
        Account(
            username=data["account"]["username"],
            email=data["account"]["email"],
        )
        for data in __jsonize(content)
    ]


def parse_tweet_data(content: bytes, account: Account) -> List[Tweet]:
    return [
        Tweet(
            id=data["tweet"]["id"],
            account_id=account.username,
            full_text=data["tweet"]["full_text"],
            favorite_count=int(data["tweet"]["favorite_count"]),
            retweet_count=int(data["tweet"]["retweet_count"]),
            retweeted=data["tweet"]["retweeted"],
            lang=data["tweet"]["lang"],
            created_at=parse_date(data["tweet"]["created_at"]),
        )
        for data in __jsonize(content)
    ]
