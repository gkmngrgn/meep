import datetime
import sys
import zipfile
from collections import namedtuple
from typing import Optional

import click

from meep.archive import parse_account_data, parse_tweet_data
from meep.browser import delete_tweets
from meep.config import DB_PATH
from meep.database import MeepDatabase
from meep.printer import format_tweet

AccountReview = namedtuple(
    "AccountReview",
    ("tweet_count", "max_favorite", "max_retweet", "max_self_reply"),
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


TWEET_TYPE_MAP: dict[str, tuple[Optional[bool], Optional[bool]]] = {
    "all": (None, None),
    "reply": (True, None),
    "original": (False, False),
    "retweet": (None, True),
}


@run.command()
@click.option("--show-tweets/--hide-tweets", default=False)
@click.option("--keyword", default="")
@click.option("--max-favorite", default=0)
@click.option("--max-retweet", default=0)
@click.option("--year", default=datetime.date.today().year)
@click.option("--order-by", default="-created_at")
@click.option(
    "--tweet-type",
    type=click.Choice(["all", "reply", "original", "retweet"]),
    default="all",
    help="Filter by tweet type: all, reply, original, or retweet.",
)
@click.option("--max-self-reply", default=0)
def analyze(  # pylint: disable=too-many-arguments
    show_tweets: bool,
    keyword: str,
    max_favorite: int,
    max_retweet: int,
    year: int,
    order_by: str,
    tweet_type: str,
    max_self_reply: int,
) -> None:
    tweets = MeepDatabase().filter_tweets(
        keyword=keyword,
        max_fav_count=max_favorite,
        max_rt_count=max_retweet,
        year=year,
        order_by=order_by,
        is_reply=TWEET_TYPE_MAP[tweet_type][0],
        is_retweet=TWEET_TYPE_MAP[tweet_type][1],
        max_self_reply_count=max_self_reply,
    )

    review = AccountReview(0, 0, 0, 0)

    for tweet in tweets:
        review = AccountReview(
            tweet_count=review.tweet_count + 1,
            max_favorite=max(review.max_favorite, tweet.favorite_count),
            max_retweet=max(review.max_retweet, tweet.retweet_count),
            max_self_reply=max(review.max_self_reply, tweet.self_reply_count),
        )
        if show_tweets is True:
            click.echo(format_tweet(tweet))
        else:
            click.echo(tweet.link)

    click.echo("REVIEW:")
    click.echo(
        f"tweets: {review.tweet_count} - "
        f"max fav: {review.max_favorite} - "
        f"max rt: {review.max_retweet} - "
        f"max self-reply: {review.max_self_reply}"
    )


@run.command("delete-tweets")
@click.option("--keyword", default="")
@click.option("--max-favorite", default=0)
@click.option("--max-retweet", default=0)
@click.option("--year", default=datetime.date.today().year)
@click.option("--order-by", default="-created_at")
@click.option(
    "--tweet-type",
    type=click.Choice(["all", "reply", "original", "retweet"]),
    default="all",
    help="Filter by tweet type: all, reply, original, or retweet.",
)
@click.option("--max-self-reply", default=0)
@click.option(
    "--confirm",
    is_flag=True,
    default=False,
    help="Actually delete tweets. Without this flag, only a dry run is performed.",
)
@click.option(
    "--headless",
    is_flag=True,
    default=False,
    help="Run browser in headless mode (no visible window).",
)
def delete_tweets_cmd(
    keyword: str,
    max_favorite: int,
    max_retweet: int,
    year: int,
    order_by: str,
    tweet_type: str,
    max_self_reply: int,
    confirm: bool,
    headless: bool,
) -> None:
    meep_db = MeepDatabase()
    tweets = list(
        meep_db.filter_tweets(
            keyword=keyword,
            max_fav_count=max_favorite,
            max_rt_count=max_retweet,
            year=year,
            order_by=order_by,
            is_reply=TWEET_TYPE_MAP[tweet_type][0],
            is_retweet=TWEET_TYPE_MAP[tweet_type][1],
            max_self_reply_count=max_self_reply,
        )
    )

    if not tweets:
        click.echo("No tweets matched the given filters.")
        return

    click.echo(f"Found {len(tweets)} tweet(s) matching filters.")

    if not confirm:
        click.echo("\nDRY RUN — tweets that would be deleted:")
        for tweet in tweets:
            click.echo(f"  {tweet.link}")
        click.echo(f"\nRe-run with --confirm to delete these {len(tweets)} tweet(s).")
        return

    tweet_urls = [tweet.link for tweet in tweets]
    deleted_count = delete_tweets(tweet_urls, headless=headless)

    for tweet in tweets[:deleted_count]:
        meep_db.delete_tweet(tweet.id)

    click.echo(f"\nDone. Deleted {deleted_count}/{len(tweets)} tweet(s).")
