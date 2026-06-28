import requests
import re
from urllib.parse import urlparse

PUBLIC_API_BASE = "https://public.api.bsky.app/xrpc"
#Note: Bluesky has a free public API so I don't have to go through hoops like twitter. However in the future that could change.

def _resolve_handle_to_did(handle: str):
    url = f"{PUBLIC_API_BASE}/com.atproto.identity.resolveHandle"
    response = requests.get(url, params={"handle": handle})
    response.raise_for_status()
    return response.json()["did"]


def _parse_bluesky_url(bluesky_url: str):
    path = urlparse(bluesky_url).path
    match = re.match(r"/profile/([^/]+)/post/([^/]+)", path)
    if not match:
        return None, None
    return match.group(1), match.group(2)


def format_bluesky_post(bluesky_url: str) -> str:
    handle, rkey = _parse_bluesky_url(bluesky_url)
    if not handle or not rkey:
        print(f"Could not parse Bluesky URL: {bluesky_url}")
        return None

    try:
        did = _resolve_handle_to_did(handle)
    except requests.exceptions.RequestException as e:
        print(f"Failed to resolve handle '{handle}': {e}")
        return None

    at_uri = f"at://{did}/app.bsky.feed.post/{rkey}"

    try:
        response = requests.get(
            f"{PUBLIC_API_BASE}/app.bsky.feed.getPostThread",
            params={"uri": at_uri}
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            print("Rate limited by Bluesky (429). Skipping this URL. " + bluesky_url)
            return None
        else:
            print(f"Other error fetching Bluesky post: {bluesky_url} status code {response.status_code}")
            return None

    data = response.json()
    post = data["thread"]["post"]
    record = post["record"]

    text = re.sub(r"\s*\n\s*", " | ", record.get("text", "")).strip()
    text = re.sub(r"\|\s*\|", "|", text) 

    embed = post.get("embed", {})
    embed_type = embed.get("$type", "")

    has_image = "app.bsky.embed.images" in embed_type
    has_video = "app.bsky.embed.video" in embed_type
    is_quote = "app.bsky.embed.record" in embed_type and "app.bsky.embed.recordWithMedia" not in embed_type

    # recordWithMedia means a quote post that ALSO has its own image/video attached
    #For the future if I want a new tag for this.
    # is_record_with_media = "app.bsky.embed.recordWithMedia" in embed_type
    # if is_record_with_media:
    #     is_quote = True
    #     media = embed.get("media", {})
    #     media_type = media.get("$type", "")
    #     has_image = "app.bsky.embed.images" in media_type
    #     has_video = "app.bsky.embed.video" in media_type

    prefix = ""
    if has_video:
        prefix = "[clip] "
    elif has_image:
        prefix = "[pic] "

    if is_quote:
        prefix = "[quote] " + prefix

    return f"{prefix}{text} {bluesky_url}"