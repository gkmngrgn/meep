import textwrap

from meep.models import Tweet


def format_tweet(tweet: Tweet) -> str:
    message = (tweet.full_text or "").replace("\n", " ")
    card = f"""
    {tweet.created_at}
    {message}
    Retweet {tweet.retweet_count} - Like {tweet.favorite_count} - Self-Reply {tweet.self_reply_count}
    {tweet.link}
    """
    return textwrap.dedent(card)
