from typing import Iterable, List, Optional

from sqlalchemy import create_engine, extract, text
from sqlalchemy.orm import Session

from meep.config import CONFIG_DIR, DB_PATH
from meep.models import Account, Base, Tweet


class MeepDatabase:
    def __init__(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(
            f"sqlite+pysqlite:///{DB_PATH}", echo=True, future=True
        )

        if not DB_PATH.exists():
            Base.metadata.create_all(self.engine)

    def get_account(self) -> Optional[Account]:
        with Session(self.engine) as session:
            account = session.query(Account).first()
        return account

    def import_accounts(self, accounts: List[Account]) -> None:
        with Session(self.engine) as session:
            accounts_filtered = [
                account
                for account in accounts
                if not session.query(
                    session.query(Account).filter_by(username=account.username).exists()
                ).scalar()
            ]
            session.add_all(accounts_filtered)
            session.commit()

    def import_tweets(self, tweets: List[Tweet]) -> None:
        with Session(self.engine) as session:
            tweets_filtered = [
                tweet
                for tweet in tweets
                if not session.query(
                    session.query(Tweet).filter_by(id=tweet.id).exists()
                ).scalar()
            ]
            session.add_all(tweets_filtered)
            session.commit()

    def filter_tweets(
        self,
        max_fav_count: int,
        max_rt_count: int,
        year: int,
        order_by: str,
    ) -> Iterable[Tweet]:
        with Session(self.engine) as session:
            tweets = (
                session.query(Tweet)
                .filter(
                    Tweet.favorite_count <= max_fav_count,
                    Tweet.retweet_count <= max_rt_count,
                    extract("year", Tweet.created_at) == year,
                )
                .order_by(text(order_by))
            )
        for tweet in tweets:
            yield tweet
