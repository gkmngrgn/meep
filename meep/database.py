from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from meep.config import CONFIG_DIR, DB_PATH
from meep.models import Base, Tweet


class MeepDatabase:
    def __init__(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(
            f"sqlite+pysqlite:///{DB_PATH}", echo=True, future=True
        )

        if not DB_PATH.exists():
            Base.metadata.create_all(self.engine)

    def import_tweets(self, tweet_list: List[Tweet]) -> None:
        tweets = []

        with Session(self.engine) as session:
            session.add_all(tweet_list)
            session.commit()

        breakpoint()
