import requests
from urllib.parse import urlparse
from unidecode import unidecode #if using unidecode version

REDDIT_DOMAINS = {"reddit.com", "v.redd.it", "i.redd.it"}

def format_reddit_post(reddit_url: str) -> str:
    base_url = reddit_url.rstrip("/")
    json_url = base_url + ".json"

    headers = {"User-Agent": "Mozilla/5.0 (compatible; reddit-helper/1.0)"}
    response = requests.get(json_url, headers=headers)
    response.raise_for_status()

    data = response.json()

    post = data[0]["data"]["children"][0]["data"]

    title = post["title"]
    external_url = post.get("url", "")
    is_self_post = post.get("is_self", False)
    is_video = post.get("is_video", False)

    prefix = "[clip] " if is_video else ""

    domain = urlparse(external_url).netloc.removeprefix("www.")
    is_external = not is_self_post and not any(domain.endswith(d) for d in REDDIT_DOMAINS)

    if is_external:
        domain_display = domain[0].upper() + domain[1:] if domain else ""
        #if you get problems with using the resulting strings that come out of this function. 
        #try using this version
        #return unidecode(f"{prefix}{title} - {domain_display} {reddit_url}") 
    #else:
        #return unidecode(f"{prefix}{title} {reddit_url}")
        return f"{prefix}{title} - {domain_display} {reddit_url}"
    else:
        return f"{prefix}{title} {reddit_url}"