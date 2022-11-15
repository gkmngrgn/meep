import datetime
import sys
import zipfile
from collections import namedtuple

import click

from meep.archive import parse_account_data, parse_tweet_data
from meep.config import DB_PATH
from meep.database import MeepDatabase
from meep.printer import format_tweet

AccountReview = namedtuple(
    "AccountReview",
    ("tweet_count", "max_favorite", "max_retweet"),
)


@click.group()
def run() -> None:
    pass


@run.command()
@click.argument("filename", type=click.Path(exists=True))
def load_data(filename: str) -> None:
    if not zipfile.is_zipfile(filename):
        click.echo(f"Not a valid zip file: {filename}")
        sys.exit(1)

    if DB_PATH.exists():
        DB_PATH.unlink()

    meep_db = MeepDatabase()
    with zipfile.ZipFile(filename) as archive:
        account = None
        for archive_file in archive.namelist():
            if archive_file.endswith("data/account.js"):
                meep_db.import_accounts(parse_account_data(archive.read(archive_file)))
                account = meep_db.get_account()
                break

        if account is None:
            click.echo("Not a valid account.")
            sys.exit(1)

        for archive_file in archive.namelist():
            if archive_file.endswith("data/tweets.js"):
                meep_db.import_tweets(
                    parse_tweet_data(archive.read(archive_file), account=account)
                )
                break

    click.echo(click.format_filename(filename))


@run.command()
@click.option("--show-tweets/--hide-tweets", default=False)
@click.option("--max-favorite", default=0)
@click.option("--max-retweet", default=0)
@click.option("--year", default=datetime.date.today().year)
@click.option("--order-by", default="-created_at")
def analyze(
    show_tweets: bool,
    max_favorite: int,
    max_retweet: int,
    year: int,
    order_by: str,
) -> None:
    tweets = MeepDatabase().filter_tweets(
        max_fav_count=max_favorite,
        max_rt_count=max_retweet,
        year=year,
        order_by=order_by,
    )

    review = AccountReview(0, 0, 0)

    for tweet in tweets:
        review = AccountReview(
            tweet_count=review.tweet_count + 1,
            max_favorite=max(review.max_favorite, tweet.favorite_count),
            max_retweet=max(review.max_retweet, tweet.retweet_count),
        )
        if show_tweets is True:
            click.echo(format_tweet(tweet))
        else:
            click.echo(tweet.link)

    click.echo("REVIEW:")
    click.echo(
        f"tweets: {review.tweet_count} - "
        f"max fav: {review.max_favorite} - "
        f"max rt: {review.max_retweet}"
    )
