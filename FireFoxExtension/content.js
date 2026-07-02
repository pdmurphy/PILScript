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

  //this is the main tweet (not quote-tweet/replies below it)
  const article = articles[0];

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
 
  if (!ogDesc) {
    return { error: "Could not find post data on page." };
  }
 
  const QUOTE_MARKER = "[contains quote post or other embedded content]";
  const isQuote = ogDesc.includes(QUOTE_MARKER);
 
  // Strip the marker (and the blank line bskyweb puts before it) back out of
  // the description so it isn't included as if it were part of the post text.
  const text = ogDesc.replace(/\s*\n\s*/g, " | ").replace(QUOTE_MARKER, "").trim();

  const hasVideo = !!ogVideo;
  const hasImage = !hasVideo && ogImage.includes("/feed_thumbnail/");
 
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