import feedparser
import requests
import os
from datetime import datetime, timezone, timedelta
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@farsianimeh"
SENT_FILE = "sent.txt"

RSS_FEEDS = [
    "https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us",
    "https://myanimelist.net/rss/news.xml"
]

def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_sent(sent):
    with open(SENT_FILE, "w") as f:
        for url in sent:
            f.write(url + "\n")

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

def get_all_news():
    news_items = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
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
    return news_items

def send_to_telegram(text):
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    r = requests.post(url, json=payload)
    print("Status:", r.status_code)

def main():
    sent = load_sent()
    all_news = get_all_news()

    for item in all_news:
        if item["link"] not in sent:
            fa_title = translate(item["title"])
            message = "اخبار انیمه\n\n" + fa_title + "\n" + item["link"] + "\n\n#anime #animenews"
            send_to_telegram(message)
            sent.add(item["link"])
            save_sent(sent)
            print("Sent:", item["title"])
            return

    print("No new items.")

if __name__ == "__main__":
    main()
