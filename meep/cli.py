import sys
import zipfile

import click

from meep.archive import parse_twitter_data
from meep.database import MeepDatabase


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
@click.option("--min-favorite", default=0)
@click.option("--tweet-count", default=1000)
@click.option("--order-by", default="-created_at")
def analyze(
    show_tweets: bool, min_favorite: int, tweet_count: int, order_by: str
) -> None:
    tweets = MeepDatabase().filter_tweets(
        min_fav_count=min_favorite,
        limit=tweet_count,
        order_by=order_by,
    )

    if show_tweets is True:
        for tweet in tweets:
            click.echo(tweet)
