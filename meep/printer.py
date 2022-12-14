import textwrap

from meep.models import Tweet


def format_tweet(tweet: Tweet) -> str:
    message = (tweet.full_text or "").replace("\n", " ")
    card = f"""
    {tweet.created_at}
    {message}
    RT {tweet.retweet_count} - <3 {tweet.favorite_count}
    {tweet.link}
    """
    return textwrap.dedent(card)
