import time
from pathlib import Path
from typing import List

import click
from playwright.sync_api import Page, sync_playwright

from meep.config import CONFIG_DIR

BROWSER_STATE_DIR: Path = CONFIG_DIR / "browser-state"
DELETE_DELAY_SECONDS: float = 3.0


def _ensure_logged_in(page: Page) -> None:
    page.goto("https://x.com/home")
    page.wait_for_load_state("networkidle")

    if "/login" in page.url or page.locator('[data-testid="loginButton"]').count() > 0:
        click.echo("You are not logged in. Please log in to X in the browser window.")
        click.echo("Waiting for login... (press Enter here after you log in)")
        input()
        page.wait_for_load_state("networkidle")

        if "/login" in page.url:
            raise click.ClickException("Login failed. Please try again.")

    click.echo("Logged in successfully.")


def _delete_single_tweet(page: Page, tweet_url: str) -> bool:
    page.goto(tweet_url)
    page.wait_for_load_state("networkidle")

    # Click the "more" menu (three dots) on the tweet
    more_button = page.locator('[data-testid="caret"]').first
    if more_button.count() == 0:
        click.echo(f"  Could not find menu button for {tweet_url}")
        return False

    more_button.click()
    page.wait_for_timeout(500)

    # Click "Delete" in the dropdown menu
    delete_option = page.get_by_role("menuitem").filter(has_text="Delete")
    if delete_option.count() == 0:
        click.echo(f"  No delete option found (may not be your tweet): {tweet_url}")
        page.keyboard.press("Escape")
        return False

    delete_option.click()
    page.wait_for_timeout(500)

    # Confirm deletion in the dialog
    confirm_button = page.locator('[data-testid="confirmationSheetConfirm"]')
    if confirm_button.count() == 0:
        click.echo(f"  No confirmation dialog found: {tweet_url}")
        return False

    confirm_button.click()
    page.wait_for_timeout(1000)
    return True


def delete_tweets(tweet_urls: List[str], headless: bool = False) -> int:
    BROWSER_STATE_DIR.mkdir(parents=True, exist_ok=True)

    deleted_count = 0
    total = len(tweet_urls)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_STATE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 720},
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            _ensure_logged_in(page)

            for i, url in enumerate(tweet_urls, start=1):
                click.echo(f"[{i}/{total}] Deleting {url} ...")
                if _delete_single_tweet(page, url):
                    deleted_count += 1
                    click.echo("  Deleted.")
                else:
                    click.echo("  Skipped.")

                if i < total:
                    time.sleep(DELETE_DELAY_SECONDS)
        finally:
            context.close()

    return deleted_count
