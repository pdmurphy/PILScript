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
  //Use textContent instead of innerText - innerText inserts line breaks at
  //block-level element boundaries (like the divs wrapping @mentions), even
  //though there's no actual newline in the tweet. textContent avoids that.
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

//Listen for message from popup
browser.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "getPostData") {
    sendResponse(getRedditPostData());
  } else if (msg.action === "getTweetData") {
    sendResponse(getTweetData());
  }
});