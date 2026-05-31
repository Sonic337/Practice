import os
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
RADAR_RSS_URL = "https://feeds.feedburner.com/oreilly/radar/atom"

TOPIC_LIMIT = 5
HN_FETCH_LIMIT = 250
MIN_POINTS = 100
MIN_COMMENTS = 50

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


def is_ai_topic(text):
    lower = text.lower()
    return any(re.search(keyword, lower) for keyword in AI_KEYWORDS)


def engagement_score(points, comments):
    return points + comments * 2


def fetch_hn_story(story_id):
    response = requests.get(HN_ITEM_URL.format(id=story_id), timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_hn_ai_stories():
    response = requests.get(HN_TOP_STORIES_URL, timeout=15)
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

            points = item.get("score") or 0
            comments = item.get("descendants") or 0
            if points < MIN_POINTS and comments < MIN_COMMENTS:
                continue

            url = item.get("url") or f"https://news.ycombinator.com/item?id={item['id']}"
            stories.append(
                {
                    "title": title,
                    "url": url,
                    "source": "Hacker News",
                    "points": points,
                    "comments": comments,
                    "engagement": engagement_score(points, comments),
                }
            )

    return stories


def fetch_radar_ai_stories():
    response = requests.get(RADAR_RSS_URL, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    channel = root.find("channel")
    if channel is None:
        return []

    stories = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title:
            continue

        categories = [
            (cat.text or "").strip()
            for cat in item.findall("category")
            if cat.text
        ]
        is_ai = "AI & ML" in categories or is_ai_topic(title)
        if not is_ai:
            continue

        subtitle_el = item.find("{https://www.oreilly.com/rss/custom}subtitle")
        subtitle = (subtitle_el.text or "").strip() if subtitle_el is not None else ""
        display_title = f"{title} — {subtitle}" if subtitle else title

        # Curated feed: baseline engagement meets the trending threshold.
        points = MIN_POINTS
        comments = MIN_COMMENTS
        stories.append(
            {
                "title": display_title,
                "url": link,
                "source": "O'Reilly Radar",
                "points": points,
                "comments": comments,
                "engagement": engagement_score(points, comments),
            }
        )

    return stories


def dedupe_stories(stories):
    seen = set()
    unique = []
    for story in stories:
        key = re.sub(r"\W+", "", story["title"].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(story)
    return unique


def rank_top_stories(stories, limit=TOPIC_LIMIT):
    return sorted(dedupe_stories(stories), key=lambda s: s["engagement"], reverse=True)[
        :limit
    ]


def suggest_angles(topic):
    return [t.format(topic=topic) for t in ANGLE_TEMPLATES]


def format_story(story, index):
    lines = [
        f"{index}. {story['title']}",
        f"   {story['source']} · {story['points']} pts · {story['comments']} comments · engagement {story['engagement']}",
        f"   {story['url']}",
        "   Content angles:",
    ]
    for angle in suggest_angles(story["title"]):
        lines.append(f"   • {angle}")
    return lines


def build_report(stories):
    now = datetime.now().strftime("%A, %B %d, %Y")
    lines = [
        f"AI Content Ideas — {now}",
        f"Top {len(stories)} trending AI topics (HN mindshare + O'Reilly Radar)",
        "",
    ]

    if not stories:
        lines.append("No trending AI stories matched the filters today.")
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

    hn_stories = fetch_hn_ai_stories()
    radar_stories = fetch_radar_ai_stories()
    top_stories = rank_top_stories(hn_stories + radar_stories)

    report = build_report(top_stories)
    print(report)
    print()

    send_to_telegram(report)
    print("Content ideas sent to Telegram.")


if __name__ == "__main__":
    main()
