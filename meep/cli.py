import zipfile

import click
from sqlalchemy import select

from meep.archive import parse_twitter_data
from meep.database import MeepDatabase, Tweet


@click.group()
def run() -> None:
    print("it worked.")


@run.command()
@click.argument("filename", type=click.Path(exists=True))
def load_data(filename: str) -> None:
    if not zipfile.is_zipfile(filename):
        click.echo(f"Not a valid zip file: {filename}")
        exit(1)

    meep_db = MeepDatabase()

    with zipfile.ZipFile(filename) as z:
        for z_file in z.namelist():
            if z_file.endswith("data/tweets.js"):
                content = z.read(z_file)
                tweet_data = parse_twitter_data(content)
                meep_db.import_tweets(tweet_data)
                break

    click.echo(click.format_filename(filename))


@run.command()
def analyze() -> None:
    meep_db = MeepDatabase()
    statement = select(Tweet).where(Tweet.favorite_count > 1).order_by(Tweet.created_at)
    with meep_db.engine.connect() as connection:
        result = connection.execute(statement).fetchall()
    breakpoint()
