import feedparser
import requests
import os
import random
from datetime import datetime, timezone, timedelta
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@farsianimeh"
SENT_FILE = "sent.txt"
MODE_FILE = "mode.txt"

RSS_FEEDS = [
    "https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us",
    "https://myanimelist.net/rss/news.xml"
]

KIDS_ANIME = [
    {"title": "Doraemon", "fa": "دورایمون", "link": "https://www.crunchyroll.com/doraemon", "desc": "ماجراهای نوبیتا و ربات آینده‌نگر او دورایمون"},
    {"title": "Pokemon", "fa": "پوکمون", "link": "https://www.crunchyroll.com/pokemon", "desc": "سفر اش برای تبدیل شدن به استاد پوکمون"},
    {"title": "Hamtaro", "fa": "همتارو", "link": "https://www.crunchyroll.com/hamtaro", "desc": "ماجراهای دسته‌ای از همسترهای کوچولو"},
    {"title": "Cardcaptor Sakura", "fa": "ساکورا کارت کاپتور", "link": "https://www.crunchyroll.com/cardcaptor-sakura", "desc": "دختری که کارت‌های جادویی پراکنده را جمع‌آوری می‌کند"},
    {"title": "My Neighbor Totoro", "fa": "همسایه من توتورو", "link": "https://www.netflix.com/title/70023671", "desc": "دو خواهر با موجودات جادویی جنگل آشنا می‌شوند"},
    {"title": "Spirited Away", "fa": "شهر اشباح", "link": "https://www.netflix.com/title/60023642", "desc": "دختری در دنیای ارواح گیر می‌افتد"},
    {"title": "Kiki Delivery Service", "fa": "سرویس تحویل کیکی", "link": "https://www.netflix.com/title/60032294", "desc": "جادوگر جوانی کسب‌وکار پست جادویی راه‌اندازی می‌کند"},
    {"title": "Chi Sweet Home", "fa": "خانه شیرین چی", "link": "https://www.crunchyroll.com/chis-sweet-home", "desc": "ماجراهای بامزه یک گربه کوچولوی گم‌شده"},
    {"title": "Yotsuba", "fa": "یوتسوبا", "link": "https://myanimelist.net/manga/104", "desc": "دختر کوچولویی که هر روز دنیا را کشف می‌کند"},
    {"title": "Sailor Moon", "fa": "ملوان ماه", "link": "https://www.crunchyroll.com/sailor-moon", "desc": "دختران جنگجو برای حفاظت از زمین تلاش می‌کنند"},
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

def get_mode():
    if not os.path.exists(MODE_FILE):
        return "news"
    with open(MODE_FILE, "r") as f:
        return f.read().strip()

def save_mode(mode):
    with open(MODE_FILE, "w") as f:
        f.write(mode)

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
                        news_items.append({"title": entry.title, "link": entry.link})
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

def post_news():
    sent = load_sent()
    all_news = get_all_news()
    for item in all_news:
        if item["link"] not in sent:
            fa_title = translate(item["title"])
            message = "اخبار انیمه\n\n" + fa_title + "\n" + item["link"] + "\n\n#anime #animenews"
            send_to_telegram(message)
            sent.add(item["link"])
            save_sent(sent)
            print("News sent:", item["title"])
            return
    print("No new news.")

def post_anime():
    sent = load_sent()
    unseen = [a for a in KIDS_ANIME if a["link"] not in sent]
    if not unseen:
        sent = set()
        unseen = KIDS_ANIME
    anime = random.choice(unseen)
    message = (
        "معرفی انیمه کودکان\n\n"
        + anime["fa"] + "\n"
        + anime["desc"] + "\n\n"
        + "تماشای رایگان:\n" + anime["link"] + "\n\n"
        + "#anime #kids #animekids"
    )
    send_to_telegram(message)
    sent.add(anime["link"])
    save_sent(sent)
    print("Anime sent:", anime["title"])

def main():
    mode = get_mode()
    print("Mode:", mode)
    if mode == "news":
        post_news()
        save_mode("anime")
    else:
        post_anime()
        save_mode("news")

if __name__ == "__main__":
    main()
