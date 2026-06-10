from playwright.sync_api import sync_playwright
#from playwright_stealth import stealth_sync
from urllib.parse import urlparse
#not implementing headless currently.
from BrowserUtility import get_browser

def format_tweet(twitter_url: str) -> str:
    browser = get_browser()
    page = browser.new_page()

    try:
        page.goto(twitter_url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"Failed to load tweet page: {e}")
        browser.close()
        return None

    # Wait for the tweet text to appear
    try:
        # Wait for the article to load instead
        page.wait_for_selector("article", timeout=15000)
    except Exception:
        print("Could not find tweet content. Skipping. " + twitter_url) 
        browser.close()
        return None

    # Get tweet text and replace newlines
    #tweet_el = page.locator("[data-testid='tweetText']")
    #check if quote tweet and set boolean flag. if locator finds more than 1 result. 
    is_quote_tweet = page.locator("article div[data-href]").count() > 0
    # Tweet text - first dir=auto div inside article
    text = page.locator("article div[dir='auto']").first.inner_text().replace("\n", " | ")

    # Detect media
    # Give media elements time to load after tweet text appears
    page.wait_for_timeout(200)
    has_video = page.locator("article video").count() > 0
    has_image = page.locator("article a[aria-label='Image']").count() > 0

    page.close()

    #I think technically if the tweet is a quotetweet, and has a picture and clip, it might have both labels.
    #something to potentially fix or just leave as is.
    if has_video:
        prefix = "[clip] "
    elif has_image:
        prefix = "[pic] "
    else:
        prefix = ""
    #after media label, add quotetweet label if applicable.
    if is_quote_tweet:
        prefix = "[quotetweet]" + prefix

    return f"{prefix}{text} {twitter_url}"