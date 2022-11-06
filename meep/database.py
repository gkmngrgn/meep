from typing import Any, Dict

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

meta = MetaData()

tweets = Table(
    "tweets",
    meta,
    Column("id", String, primary_key=True),
    Column("full_text", String),
    Column("favorite_count", Integer),
    Column("retweet_count", Integer),
    Column("retweeted", Boolean),
    Column("lang", String),
    Column("created_at", DateTime),
)


class MeepDatabase:
    def __init__(self) -> None:
        # TODO: check if the database is created.
        engine = create_engine("sqlite+pysqlite:///meep.sqlite", echo=True, future=True)
        meta.create_all(engine)

    def import_tweets(self, tweet_data: Dict[str, Any]) -> None:
        breakpoint()
