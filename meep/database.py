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
        with Session(self.engine) as session:
            tweet_list_filtered = [
                tweet
                for tweet in tweet_list
                if not session.query(
                    session.query(Tweet).filter_by(id=tweet.id).exists()
                ).scalar()
            ]
            session.add_all(tweet_list_filtered)
            session.commit()
