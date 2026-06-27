import feedparser
import requests
import os
from datetime import datetime, timezone, timedelta
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@farsianimeh"

RSS_FEEDS = [
    "https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us",
    "https://myanimelist.net/rss/news.xml"
]

def translate(text):
    try:
        url = "https://api.mymemory.translated.net/get"
        r = requests.get(url, params={"q": text[:400], "langpair": "en|fa"}, timeout=10)
        result = r.json()
        translated = result["responseData"]["translatedText"]
        if translated and len(translated) > 5:
            return translated
    except:
        pass
    return text

def get_recent_news(hours=12):
    news_items = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                try:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    if published > cutoff:
                        news_items.append({
                            "title": entry.title,
                            "link": entry.link,
                        })
                except:
                    continue
        except:
            continue
    return news_items[:5]

def format_message(items):
    if not items:
        return None
    now = datetime.now(timezone(timedelta(hours=3, minutes=30)))
    header = f"🎌 اخبار انیمه | {now.strftime('%Y/%m/%d')}\n\n"
    body = ""
    for item in items:
        fa_title = translate(item["title"])
        time.sleep(1)
        body += f"🔸 {fa_title}\n"
        body += f"🔗 {item['link']}\n\n"
    footer = "#انیمه #اخبار_انیمه #anime"
    return header + body + footer

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    r = requests.post(url, json=payload)
    print("Status:", r.status_code)

def main():
    print("Fetching news...")
    items = get_recent_news(hours=12)
    print(f"Found {len(items)} items")
    message = format_message(items)
    if message:
        send_to_telegram(message)
        print("Sent!")
    else:
        print("No new items.")

if __name__ == "__main__":
    main()
�
