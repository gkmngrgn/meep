import json
from typing import List

from dateutil.parser import parse as parse_date

from meep.models import Tweet


def parse_twitter_data(content: bytes) -> List[Tweet]:
    start_index = content.index(b"[")
    end_index = content.rindex(b"]") + 1
    tweet_data = json.loads(content[start_index:end_index])
    return [
        Tweet(
            id=data["tweet"]["id"],
            full_text=data["tweet"]["full_text"],
            favorite_count=int(data["tweet"]["favorite_count"]),
            retweet_count=int(data["tweet"]["retweet_count"]),
            retweeted=data["tweet"]["retweeted"],
            lang=data["tweet"]["lang"],
            created_at=parse_date(data["tweet"]["created_at"]),
        )
        for data in tweet_data
    ]
