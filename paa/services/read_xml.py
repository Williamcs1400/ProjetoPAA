import feedparser
import threading
import database.database_operations as db 

URL = 'https://g1.globo.com/rss/g1/' # URL do feed
INTERVAL = 60                        # tempo de intervalo entre as chamadas leituras do feed
last_news = []                       # 

def read_news():
    print('Lendo notícias...')
    threading.Timer(INTERVAL, read_news).start()

    NewsFeed = feedparser.parse(URL)

    last_news.clear()
    for entry in NewsFeed.entries:
        # salvar ultimas noticias
        last_news.append({'title': entry.title, 'link': entry.link})

        # inserir noticia no banco de dados
        db.insert_news(entry.title, entry.summary)

def get_last_news():
    return last_news