const REDDIT_DOMAINS = new Set(["reddit.com", "v.redd.it", "i.redd.it"]);

function getDomain(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function isRedditDomain(domain) {
  return [...REDDIT_DOMAINS].some(d => domain.endsWith(d));
}

function formatTweetResult(tweet) {
  const text         = tweet.text || "";
  const hasVideo     = tweet.hasVideo || false;
  const hasImage     = tweet.hasImage || false;
  const isQuoteTweet = tweet.isQuoteTweet || false;
  const pageUrl       = tweet.url;

  let prefix = "";
  if (hasVideo) {
    prefix = "[clip] ";
  } else if (hasImage) {
    prefix = "[pic] ";
  }
  if (isQuoteTweet) {
    prefix = "[quotetweet] " + prefix;
  }

  return `${prefix}${text} ${pageUrl}`;
}


function formatBlueskyResult(post) {
  const text     = post.text || "";
  const hasVideo = post.hasVideo || false;
  const hasImage = post.hasImage || false;
  const isQuote  = post.isQuote || false;
  const pageUrl  = post.url;
 
  let prefix = "";
  if (hasVideo) {
    prefix = "[clip] ";
  } else if (hasImage) {
    prefix = "[pic] ";
  }
  if (isQuote) {
    // [quote], not [quotetweet] since its not a tweet
    prefix = "[quote] " + prefix;
  }
 
  return `${prefix}${text} ${pageUrl}`;
}


function formatResult(post) {
  const title    = post.title || "Unknown Title";
  const linkHref = post.linkHref || "";
  const isSelf   = post.isSelf || false;
  const isVideo  = post.isVideo || false;
  const pageUrl  = post.url;

  const prefix = isVideo ? "[clip] " : "";

  const domain = getDomain(linkHref);
  const isExternal = !isSelf && !isRedditDomain(domain);

  if (isExternal) {
    const domainDisplay = domain.charAt(0).toUpperCase() + domain.slice(1);
    return `${prefix}${title} - ${domainDisplay} ${pageUrl}`;
  } else {
    return `${prefix}${title} ${pageUrl}`;
  }
}

async function run() {
  const statusEl = document.getElementById("status");
  const resultEl = document.getElementById("result");

  const tabs = await browser.tabs.query({ active: true, currentWindow: true });
  const tab  = tabs[0];

  const isReddit  = /reddit\.com\/r\/[^/]+\/comments\//.test(tab.url);
  const isTwitter = /(twitter\.com|x\.com)\/[^/]+\/status\//.test(tab.url);
   const isBluesky = /bsky\.app\/profile\/[^/]+\/post\//.test(tab.url);

  if (!isReddit && !isTwitter && !isBluesky) {
    statusEl.textContent = "Not a Reddit post or Tweet, or Bluesky post page.";
    statusEl.className = "error";
    return;
  }


  let action;
  if (isReddit) {
    action = "getPostData";
  } else if (isTwitter) {
    action = "getTweetData";
  } else {
    action = "getBlueskyData";
  }

  let data;
  try {
    data = await browser.tabs.sendMessage(tab.id, { action });
  } catch (err) {
    statusEl.textContent = "Could not read page. Try refreshing it.";
    statusEl.className = "error";
    return;
  }

  if (data.error) {
    statusEl.textContent = data.error;
    statusEl.className = "error";
    return;
  }

  let formatted;
  if (isReddit) {
    formatted = formatResult(data);
  } else if (isTwitter) {
    formatted = formatTweetResult(data);
  } else {
    formatted = formatBlueskyResult(data);
  }

  try {
    await navigator.clipboard.writeText(formatted);
    statusEl.textContent = "Copied to clipboard!";
    statusEl.className = "success";
    resultEl.textContent = formatted;
    resultEl.style.display = "block";
  } catch {
    statusEl.textContent = "Copy manually:";
    statusEl.className = "error";
    resultEl.textContent = formatted;
    resultEl.style.display = "block";
  }
}

run();