import feedparser
import threading
import database.database_operations as db 

URL = 'https://g1.globo.com/rss/g1/' # URL do feed
INTERVAL = 60                        # tempo de intervalo entre as chamadas leituras do feed

def read_news():
    threading.Timer(INTERVAL, read_news).start()

    NewsFeed = feedparser.parse(URL)
    for entry in NewsFeed.entries:
        db.insert_news(entry.title, entry.summary)
