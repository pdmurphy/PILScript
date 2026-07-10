// Reads post data directly from the already-loaded Reddit page DOM
function getRedditPostData() {
  const url = window.location.href;

  //old.reddit.com
  if (window.location.hostname === "old.reddit.com") {
    const titleEl = document.querySelector("a.title");
    if (!titleEl) return { error: "Could not find post title on page." };

    const title = titleEl.innerText.trim();
    const linkHref = titleEl.href || "";
    const isSelf = titleEl.classList.contains("self");
    const isVideo = !!document.querySelector(".video-player, .reddit-video-player");

    return { title, linkHref, isSelf, isVideo, url };
  }

  //www.reddit.com (new Reddit)
  const ldScript = document.querySelector('script[type="application/ld+json"]');
  if (ldScript) {
    try {
      const data = JSON.parse(ldScript.textContent);
      const title = data.headline || data.name || "";
      const linkHref = data.url || "";
      const isVideo = data["@type"] === "VideoObject";
      const isSelf = !linkHref || linkHref.includes("reddit.com");
      if (title) return { title, linkHref, isSelf, isVideo, url };
    } catch {}
  }

  //if problem read from the page's __NEXT_DATA__
  const nextScript = document.getElementById("__NEXT_DATA__");
  if (nextScript) {
    try {
      const data = JSON.parse(nextScript.textContent);
      const post = data?.props?.pageProps?.post || 
                   data?.props?.pageProps?.postDetail?.post;
      if (post) {
        return {
          title: post.title,
          linkHref: post.url || "",
          isSelf: post.isSelf || false,
          isVideo: post.isVideo || false,
          url
        };
      }
    } catch {}
  }

  return { error: "Could not extract post data from page." };
}

function getTweetData() {
  const url = window.location.href;

  const articles = document.querySelectorAll("article");
  if (!articles.length) {
    return { error: "Could not find tweet on page. Try waiting for it to load." };
  }

  // Find the article matching the current status ID in the page URL.
  // Can't just use articles[0] as if the tweet is a reply it wont be [0].
  const statusId = window.location.pathname.match(/status\/(\d+)/)?.[1];
  const article = statusId
    ? Array.from(articles).find(a => a.querySelector(`a[href*="/status/${statusId}"]`))
    : articles[0]; // fallback to first if URL doesn't have a status ID for some reason

  //console.log(article.outerHTML); //used for debugging

  const textEl = article.querySelector("[data-testid='tweetText']") ||
                 article.querySelector("div[lang]");
  if (!textEl) {
    return { error: "Could not find tweet text on page." };
  }
  //Use textContent instead of innerText to help about line break issues.
  const text = textEl.textContent.replace(/\s*\n\s*/g, " | ").trim();

  //<video> tag only mounts once playback starts - before that,
  //Twitter shows a "previewInterstitial" thumbnail with a play button.
  const hasVideo = article.querySelector("video") !== null ||
                    article.querySelector("[data-testid='previewInterstitial']") !== null;
  const hasImage = !hasVideo && article.querySelector("a[aria-label='Image']") !== null;

  // Quote tweets show a literal "Quote" label span right before the embedded quoted tweet's container
  const isQuoteTweet = Array.from(article.querySelectorAll("span")).some(
    span => span.textContent.trim() === "Quote"
  );

  return { text, hasVideo, hasImage, isQuoteTweet, url };
}

// Bluesky we have to read via  <meta property="og:..."> 
// distinguish own-image vs own-video vs quote-post vs quote-with-own-media:
//   - og:image path contains "feed_thumbnail" -> post has its own image
//   - og:image path contains "avatar_thumbnail" (or no og:image) -> no own image
//   - og:video present -> post has its own video
//   - og:description containing the literal "[contains quote post or other
//     embedded content]" marker -> post is quoting/embedding another post
// These two signals are independent, so a post can be both (own image/video
// AND a quote) - confirmed against a real recordWithMedia example.
function getBlueskyPostData() {
  const url = window.location.href;

  const ogImage = document.querySelector('meta[property="og:image"]')?.content || "";
  const ogVideo = document.querySelector('meta[property="og:video"]')?.content || "";
  const ogDesc  = document.querySelector('meta[property="og:description"]')?.content || "";

  const QUOTE_MARKER = "[contains quote post or other embedded content]";
  const LOCKED_MARKER = "This author has chosen to make their posts visible only to people who are signed in.";

  // Public post — use og: tags (fast, reliable, no DOM needed)
  if (ogDesc && !ogDesc.includes(LOCKED_MARKER)) {
    const isQuote = ogDesc.includes(QUOTE_MARKER);
    const text = ogDesc.replace(QUOTE_MARKER, "").replace(/\s*\n\s*/g, " | ").trim();
    const hasVideo = !!ogVideo;
    const hasImage = !hasVideo && ogImage.includes("/feed_thumbnail/");
    return { text, hasVideo, hasImage, isQuote, url };
  }

  // Followers-only post — fall back to reading the live DOM
  const handle = url.match(/profile\/([^/]+)\/post/)?.[1];
  if (!handle) return { error: "Could not find post data on page." };

  const post = document.querySelector(`[data-testid="postThreadItem-by-${handle}"]`);
  if (!post) return { error: "Could not find post data on page. Try waiting for it to load." };

  const quoteEl = post.querySelector('div[role="link"]');
  const isQuote  = !!quoteEl;

  const hasVideo = !![...post.querySelectorAll("video, [data-testid='previewInterstitial']")]
    .some(el => !quoteEl?.contains(el));

  const hasImage = !hasVideo && [...post.querySelectorAll("img[src*='feed_thumbnail']")]
    .some(img => !quoteEl?.contains(img));

  // Find handle div as position anchor to exclude display name above it
  const UI_STRINGS = new Set([
    "Follow", "Unfollow",
    "Everybody can reply", "Nobody can reply", "Mentioned accounts can reply"
  ]);

  const handleDiv = [...post.querySelectorAll('div')].find(d =>
    d.children.length === 0 &&
    new RegExp(`@${handle}`).test(d.textContent)
  );

  const textNodes = [...post.querySelectorAll('div')].filter(d => {
    if (d.children.length !== 0) return false;
    if (quoteEl?.contains(d)) return false;
    if (handleDiv && !(handleDiv.compareDocumentPosition(d) & Node.DOCUMENT_POSITION_FOLLOWING)) return false;
    const t = d.textContent.trim();
    if (t.length === 0) return false;
    if (UI_STRINGS.has(t)) return false;
    if (/^[\u200e\u200f\u202a\u202c]*@\S+[\u200e\u200f\u202a\u202c]*$/.test(t)) return false;
    if (/\d:\d\d\s*(AM|PM)/.test(t)) return false;
    if (/^\d+(\.\d+)?[KM]?$/.test(t)) return false;
    if (/^\d+:\d\d[\d:]* \/ \d+:\d\d[\d:]*$/.test(t)) return false;  // this is if video post has no text the length of video will be here instead of text.
    return true;
  });

  const text = textNodes.map(d => d.textContent.trim().replace(/\s*\n\s*/g, " | ")).join(" | ");

  return { text, hasVideo, hasImage, isQuote, url };
}

function getYouTubeData() {
  const url = window.location.href;

  const rawTitle = document.querySelector('meta[property="og:title"]')?.content || "";
  const duration = document.querySelector('meta[itemprop="duration"]')?.content || "";

  if (!rawTitle || !duration) {
    return { error: "Could not find video data on page." };
  }

  // og:title sometimes has " - YouTube" appended depending on page context
  const title = rawTitle.replace(/\s*-\s*YouTube\s*$/, "").trim();

  // ISO 8601 duration (e.g. PT1H2M35S) -> "1:02:35" or "29:35"
  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) {
    return { error: "Could not parse video duration." };
  }
  const hours   = parseInt(match[1] || "0");
  const minutes = parseInt(match[2] || "0");
  const seconds = parseInt(match[3] || "0");

  const pad = n => String(n).padStart(2, "0");
  const timestamp = hours > 0
    ? `${hours}:${pad(minutes)}:${pad(seconds)}`
    : `${minutes}:${pad(seconds)}`;

  return { title, timestamp, url };
}

//Listen for message from popup
browser.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "getPostData") {
    sendResponse(getRedditPostData());
  } else if (msg.action === "getTweetData") {
    sendResponse(getTweetData());
  } else if (msg.action === "getBlueskyData") {
    sendResponse(getBlueskyPostData());
  } else if (msg.action === "getYouTubeData") {
    sendResponse(getYouTubeData());
  }
});