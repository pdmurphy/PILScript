import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse

NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
]

def format_tweet(twitter_url: str) -> str:
    # Extract the path from the twitter/x URL to build nitter URL
    path = urlparse(twitter_url).path

#THIS CURRENTLY DOES NOT WORK DESPITE MULTIPLE CHANGES. 

    html = None
    for instance in NITTER_INSTANCES:
        try:
            nitter_url = instance + path
            headers = {"User-Agent": "Mozilla/5.0 (compatible; tweet-helper/1.0)"}
            session = requests.Session()
            # "Visit" the homepage first to pick up any required cookies
            session.get(instance, headers=headers, timeout=10)
            # Then fetch the actual tweet
            response = session.get(nitter_url, headers=headers, timeout=15, allow_redirects=True)
            #response = requests.get(nitter_url, headers=headers, timeout=15, allow_redirects=True)
            time.sleep(3)  # Give it a moment to settle
            if response.status_code == 429:
                print("Rate limited by Twitter/Nitter (429). Skipping this URL. " + nitter_url)
                return None
            if response.status_code == 200:
                print(response.content)
                print("htmltext")
                print(response.text)
                html = response.content
                break
        except requests.exceptions.RequestException:
            print("request exception")
            continue  # Try next instance

    if html is None:
        print("All Nitter instances failed or are unavailable. Skipping.")
        return None

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all("div", class_=True):
        print("tag " + tag)
        print(tag["class"], "-->", tag.get_text(strip=True)[:80])

    # data = requests.get("https://www.uniprot.org/uniprot/P28653.fasta").content
    # print(data)

    print(soup.find_all)
    print("findall above^")

    # Tweet text lives in div.tweet-content
    content_div = soup.find("div", class_="tweet-content")
    if not content_div:
        print("Could not find tweet content. Skipping.")
        return None

    text = content_div.get_text(strip=True).replace("\n", " | ")

    # Detect media type
    has_video = soup.find("div", class_="attachment video-container") is not None
    has_image = soup.find("div", class_="attachment image") is not None

    if has_video:
        prefix = "[clip] "
    elif has_image:
        prefix = "[pic] "
    else:
        prefix = ""

    return f"{prefix}{text} {twitter_url}"