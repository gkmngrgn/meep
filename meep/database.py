import limbo
from typing import Iterable, List, Optional
from contextlib import contextmanager

from meep.config import CONFIG_DIR, DB_PATH
from meep.models import Account, Tweet


@contextmanager
def db_cursor():
    connection = limbo.connect(str(DB_PATH))
    try:
        cur = connection.cursor()
        yield cur
    except Exception as e:
        connection.rollback()
        raise e
    else:
        connection.commit()
    finally:
        connection.close()


class MeepDatabase:
    def __init__(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        self.connection = limbo.connect(str(DB_PATH))
        self.cursor = self.connection.cursor()
        self.init_db()

    def init_db(self) -> None:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS account (
                username TEXT PRIMARY KEY UNIQUE,
                email TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS post (
                id TEXT PRIMARY KEY UNIQUE,
                account_id TEXT NOT NULL,
                full_text TEXT,
                favorite_count INTEGER,
                retweet_count INTEGER,
                retweeted BOOLEAN,
                lang TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES account (username)
            );
            """,
        ]

        for statement in statements:
            breakpoint()
            self.cursor.execute(statement)

    def get_account(self) -> Optional[Account]:
        response = self.cursor.execute("SELECT username, email FROM account LIMIT 1")
        row = response.fetchone()
        return Account.from_row(row) if row else None

    def import_accounts(self, accounts: List[Account]) -> None:
        accounts_filtered = [
            account
            for account in accounts
            if not self.cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM account WHERE username = ?)", (account.username,)
            ).fetchone()[0]
        ]
        self.cursor.executemany(
            "INSERT INTO account (username, email) VALUES (?, ?)",
            [account.to_row() for account in accounts_filtered],
        )

    def import_tweets(self, tweets: List[Tweet]) -> None:
        tweets_filtered = [
            tweet
            for tweet in tweets
            if not self.cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM post WHERE id = ?)", (tweet.id,)
            ).fetchone()[0]
        ]
        self.cursor.executemany(
            """
            INSERT INTO post (
                id, account_id, full_text, favorite_count, retweet_count, retweeted, lang, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [tweet.to_row() for tweet in tweets_filtered],
        )

    def filter_tweets(  # pylint: disable=too-many-arguments
        self,
        keyword: str,
        max_fav_count: int,
        max_rt_count: int,
        year: int,
        order_by: str,
    ) -> Iterable[Tweet]:
        tweets = self.cursor.execute(
            f"""
            SELECT * FROM post
            WHERE favorite_count <= ?
                AND retweet_count <= ?
                AND strftime('%Y', created_at) = ?
                AND full_text LIKE ?
            ORDER BY {order_by};
            """,
            (max_fav_count, max_rt_count, str(year), f"%{keyword}%"),
        )

        for tweet in tweets:
            yield Tweet.from_row(tweet)
