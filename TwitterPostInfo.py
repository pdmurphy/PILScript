from playwright.sync_api import sync_playwright
#from playwright_stealth import stealth_sync
from urllib.parse import urlparse

def format_tweet(twitter_url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) #true is trying stealth sync
        page = browser.new_page()
        #stealth_sync(page)

        try:
            page.goto(twitter_url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"Failed to load tweet page: {e}")
            browser.close()
            return None

        # Wait for the tweet text to appear
        try:
            page.wait_for_selector("[data-testid='tweetText']", timeout=15000)
        except Exception:
            print("Could not find tweet content. Skipping.")
            browser.close()
            return None

        # Get tweet text and replace newlines
        # print("debugs")
        # print( page.locator("[data-testid='tweetText']"))
        # print("Page title:", page.title())
        # print("Page URL:", page.url)
        tweet_el = page.locator("[data-testid='tweetText']")
        print("count " + str(page.locator("[data-testid='tweetText']").count()))
        is_quote_tweet = page.locator("[data-testid='tweetText']").count() > 1
        print(is_quote_tweet)
        text = tweet_el.first.inner_text().replace("\n", " | ")
# page.locator("[data-testid='tweetText']").first.inner_text().replace("\n", " | ")
#text = tweet_el.inner_text().replace("\n", " | ")
        # Detect media
        has_video = page.locator("[data-testid='videoPlayer']") is not None
        has_image = page.locator("[data-testid='tweetPhoto']") is not None

        browser.close()

    if has_video:
        prefix = "[clip] "
    elif has_image:
        prefix = "[pic] "
    else:
        prefix = ""

    if is_quote_tweet:
        prefix = "[quotetweet]" + prefix

    # print("prefix " + prefix)
    # print("text + " + text)
    return f"{prefix}{text} {twitter_url}"