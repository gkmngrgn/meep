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
