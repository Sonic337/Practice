import os
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ContentIdeasBot/1.0; +https://github.com/)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# The Verge's /ai-artificial-intelligence/rss/ path 404s; /rss/ai-artificial-intelligence/ works.
VERGE_RSS_URLS = (
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
)

RSS_SOURCES = (
    ("MIT Technology Review", ("https://www.technologyreview.com/feed/",), True),
    ("The Verge", VERGE_RSS_URLS, False),
    ("Wired", ("https://www.wired.com/feed/tag/ai/latest/rss",), False),
    ("VentureBeat", ("https://venturebeat.com/category/ai/feed/",), False),
    ("TechCrunch", ("https://techcrunch.com/category/artificial-intelligence/feed/",), False),
)

SOURCE_CREDIBILITY = {
    "MIT Technology Review": 95,
    "Wired": 90,
    "The Verge": 85,
    "TechCrunch": 80,
    "VentureBeat": 75,
    "Hacker News": 70,
}

TOPIC_LIMIT = 5
HN_FETCH_LIMIT = 250
HOURS_WINDOW = 24
TITLE_SIMILARITY_THRESHOLD = 0.85

AI_KEYWORDS = (
    r"\bai\b",
    r"\bartificial intelligence\b",
    r"\bmachine learning\b",
    r"\bllm\b",
    r"\blarge language model\b",
    r"\bgpt\b",
    r"\bopenai\b",
    r"\banthropic\b",
    r"\bdeepseek\b",
    r"\bagentic\b",
    r"\bneural\b",
    r"\bchatbot\b",
    r"\bgenerative\b",
    r"\btransformer\b",
    r"\bdiffusion\b",
    r"\bmodel training\b",
    r"\bfine-tuning\b",
    r"\brag\b",
    r"\bmcp\b",
)

ANGLE_TEMPLATES = [
    "Breaking down the story: {topic}",
    "What this means for AI builders — practical implications in plain English",
    "5 quick takeaways worth sharing from: {topic}",
    "Hot take: why this is dominating AI mindshare right now",
    "Beginner FAQ: the essentials you need to know about {topic}",
]


def require_config():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise SystemExit("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env")


def cutoff_utc():
    return datetime.now(timezone.utc) - timedelta(hours=HOURS_WINDOW)


def is_ai_topic(text):
    lower = text.lower()
    return any(re.search(keyword, lower) for keyword in AI_KEYWORDS)


def parse_published_at(text):
    if not text:
        return None
    text = text.strip()
    try:
        normalized = text.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None


def ensure_utc(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def within_last_24h(dt):
    if dt is None:
        return False
    return ensure_utc(dt) >= cutoff_utc()


def normalize_title(title):
    return re.sub(r"\W+", " ", title.lower()).strip()


def titles_similar(a, b, threshold=TITLE_SIMILARITY_THRESHOLD):
    return (
        SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()
        >= threshold
    )


def source_credibility(source):
    return SOURCE_CREDIBILITY.get(source, 60)


def rank_score(story, now=None):
    now = now or datetime.now(timezone.utc)
    credibility = story["credibility"]
    published = ensure_utc(story["published_at"])
    age_hours = max(0.0, (now - published).total_seconds() / 3600)
    recency = max(0.0, 1.0 - age_hours / HOURS_WINDOW)
    return credibility * 0.65 + recency * 100 * 0.35


def make_story(title, url, source, published_at, **extra):
    credibility = source_credibility(source)
    story = {
        "title": title,
        "url": url,
        "source": source,
        "published_at": ensure_utc(published_at),
        "credibility": credibility,
        **extra,
    }
    story["rank_score"] = rank_score(story)
    return story


def fetch_hn_story(story_id):
    response = requests.get(
        HN_ITEM_URL.format(id=story_id), timeout=15, headers=REQUEST_HEADERS
    )
    response.raise_for_status()
    return response.json()


def fetch_hn_ai_stories():
    response = requests.get(HN_TOP_STORIES_URL, timeout=15, headers=REQUEST_HEADERS)
    response.raise_for_status()
    story_ids = response.json()[:HN_FETCH_LIMIT]

    stories = []
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(fetch_hn_story, sid): sid for sid in story_ids}
        for future in as_completed(futures):
            try:
                item = future.result()
            except requests.RequestException:
                continue

            if not item or item.get("type") != "story":
                continue

            title = (item.get("title") or "").strip()
            if not title or not is_ai_topic(title):
                continue

            story_time = item.get("time")
            if not story_time:
                continue
            published_at = datetime.fromtimestamp(story_time, tz=timezone.utc)
            if not within_last_24h(published_at):
                continue

            url = item.get("url") or f"https://news.ycombinator.com/item?id={item['id']}"
            stories.append(
                make_story(
                    title,
                    url,
                    "Hacker News",
                    published_at,
                    points=item.get("score") or 0,
                    comments=item.get("descendants") or 0,
                )
            )

    return stories


def _local_tag(element):
    tag = element.tag
    if tag.startswith("{"):
        return tag.split("}", 1)[-1]
    return tag


def _find_child(entry, local_name):
    for child in entry:
        if _local_tag(child) == local_name:
            return child
    return None


def _find_child_text(entry, local_name):
    child = _find_child(entry, local_name)
    if child is None:
        return ""
    return (child.text or "").strip()


def _entry_title(entry):
    return _find_child_text(entry, "title") or (entry.findtext("title") or "").strip()


def _entry_link(entry):
    link = _find_child_text(entry, "link") or (entry.findtext("link") or "").strip()
    if link:
        return link
    for link_el in entry.iter():
        if _local_tag(link_el) != "link":
            continue
        href = link_el.get("href")
        if not href:
            continue
        rel = link_el.get("rel", "alternate")
        if rel in ("alternate", ""):
            return href.strip()
    guid = _find_child_text(entry, "id") or (entry.findtext("guid") or "").strip()
    if guid.startswith("http"):
        return guid
    return ""


def _entry_published_at(entry):
    for local_name in ("published", "pubDate", "updated", "date"):
        text = _find_child_text(entry, local_name)
        if not text:
            text = entry.findtext(f"{{http://purl.org/dc/elements/1.1/}}{local_name}") or ""
        if text:
            parsed = parse_published_at(text)
            if parsed:
                return parsed
    return None


def _feed_entries(root):
    channel = root.find("channel")
    if channel is not None:
        return channel.findall("item")
    return root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//item")


def _parse_rss_content(content, source_name, filter_ai=False):
    root = ET.fromstring(content)
    stories = []
    for entry in _feed_entries(root):
        title = _entry_title(entry)
        if not title:
            continue

        if filter_ai and not is_ai_topic(title):
            continue

        published_at = _entry_published_at(entry)
        if not within_last_24h(published_at):
            continue

        link = _entry_link(entry)
        if not link:
            continue

        stories.append(make_story(title, link, source_name, published_at))

    return stories


def fetch_rss_stories(source_name, feed_urls, filter_ai=False):
    last_error = None
    for feed_url in feed_urls:
        try:
            response = requests.get(
                feed_url, timeout=15, headers=REQUEST_HEADERS
            )
            response.raise_for_status()
            return _parse_rss_content(response.content, source_name, filter_ai)
        except requests.RequestException as exc:
            last_error = exc
    if last_error:
        raise last_error
    return []


def fetch_all_rss_stories():
    stories = []
    with ThreadPoolExecutor(max_workers=len(RSS_SOURCES)) as pool:
        futures = {
            pool.submit(fetch_rss_stories, name, urls, filter_ai): name
            for name, urls, filter_ai in RSS_SOURCES
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                stories.extend(future.result())
            except requests.RequestException as exc:
                print(f"Warning: failed to fetch {source}: {exc}")
    return stories


def dedupe_by_title_similarity(stories):
    ranked = sorted(stories, key=lambda s: s["rank_score"], reverse=True)
    kept = []
    for story in ranked:
        if any(titles_similar(story["title"], other["title"]) for other in kept):
            continue
        kept.append(story)
    return kept


def rank_top_stories(stories, limit=TOPIC_LIMIT):
    return dedupe_by_title_similarity(stories)[:limit]


def suggest_angles(topic):
    return [t.format(topic=topic) for t in ANGLE_TEMPLATES]


def format_age(published_at):
    now = datetime.now(timezone.utc)
    hours = (now - ensure_utc(published_at)).total_seconds() / 3600
    if hours < 1:
        return f"{int(hours * 60)}m ago"
    if hours < 24:
        return f"{int(hours)}h ago"
    return f"{int(hours / 24)}d ago"


def format_story(story, index):
    lines = [
        f"{index}. {story['title']}",
        (
            f"   {story['source']} · credibility {story['credibility']} · "
            f"{format_age(story['published_at'])} · score {story['rank_score']:.1f}"
        ),
        f"   {story['url']}",
        "   Content angles:",
    ]
    for angle in suggest_angles(story["title"]):
        lines.append(f"   • {angle}")
    return lines


def build_report(stories):
    now = datetime.now().strftime("%A, %B %d, %Y")
    source_list = "HN + MIT TR, The Verge, Wired, VentureBeat, TechCrunch"
    lines = [
        f"AI Content Ideas — {now}",
        f"Top {len(stories)} AI stories (last {HOURS_WINDOW}h, {source_list})",
        "",
    ]

    if not stories:
        lines.append(f"No AI stories from the last {HOURS_WINDOW} hours matched the filters.")
        return "\n".join(lines)

    for i, story in enumerate(stories, start=1):
        lines.extend(format_story(story, i))
        if i < len(stories):
            lines.append("")

    return "\n".join(lines)


def chunk_message(text, max_len=4000):
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = []
    current_len = 0

    for line in text.splitlines():
        line_len = len(line) + 1
        if current and current_len + line_len > max_len:
            chunks.append("\n".join(current))
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len

    if current:
        chunks.append("\n".join(current))
    return chunks


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chunk in chunk_message(text):
        response = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk},
            timeout=30,
        )
        response.raise_for_status()


def main():
    require_config()

    with ThreadPoolExecutor(max_workers=2) as pool:
        hn_future = pool.submit(fetch_hn_ai_stories)
        rss_future = pool.submit(fetch_all_rss_stories)
        hn_stories = hn_future.result()
        rss_stories = rss_future.result()

    all_stories = hn_stories + rss_stories
    top_stories = rank_top_stories(all_stories)

    report = build_report(top_stories)
    print(report)
    print()

    send_to_telegram(report)
    print("Content ideas sent to Telegram.")


if __name__ == "__main__":
    main()
