import sys
import zipfile
from collections import namedtuple

import click

from meep.archive import parse_twitter_data
from meep.database import MeepDatabase
from meep.printer import format_tweet

AccountReview = namedtuple(
    "AccountReview",
    ("tweet_count", "max_favorite", "max_retweet"),
)


@click.group()
def run() -> None:
    print("it worked.")


@run.command()
@click.argument("filename", type=click.Path(exists=True))
def load_data(filename: str) -> None:
    if not zipfile.is_zipfile(filename):
        click.echo(f"Not a valid zip file: {filename}")
        sys.exit(1)

    meep_db = MeepDatabase()

    with zipfile.ZipFile(filename) as archive:
        for archive_file in archive.namelist():
            if archive_file.endswith("data/tweets.js"):
                content = archive.read(archive_file)
                tweet_data = parse_twitter_data(content)
                meep_db.import_tweets(tweet_data)
                break

    click.echo(click.format_filename(filename))


@run.command()
@click.option("--show-tweets/--hide-tweets", default=False)
@click.option("--max-favorite", default=0)
@click.option("--max-retweet", default=0)
@click.option("--tweet-count", default=1000)
@click.option("--order-by", default="-created_at")
def analyze(
    show_tweets: bool,
    max_favorite: int,
    max_retweet: int,
    tweet_count: int,
    order_by: str,
) -> None:
    tweets = MeepDatabase().filter_tweets(
        max_fav_count=max_favorite,
        max_rt_count=max_retweet,
        limit=tweet_count,
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

    click.echo("REVIEW:")
    click.echo(
        f"tweets: {review.tweet_count} - "
        f"max fav: {review.max_favorite} - "
        f"max rt: {review.max_retweet}"
    )
