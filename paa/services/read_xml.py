from os import read
import feedparser
import database.database_operations as db 

# URL = 'https://g1.globo.com/rss/g1/' # URL do feed
FEEDS_URL = ['https://g1.globo.com/rss/g1/', 'http://g1.globo.com/dynamo/carros/rss2.xml', 'http://g1.globo.com/dynamo/ciencia-e-saude/rss2.xml', 'http://g1.globo.com/dynamo/concursos-e-emprego/rss2.xml', 'http://g1.globo.com/dynamo/economia/rss2.xml', 'http://g1.globo.com/dynamo/educacao/rss2.xml', 'http://g1.globo.com/dynamo/loterias/rss2.xml', 'http://g1.globo.com/dynamo/mundo/rss2.xml', 'http://g1.globo.com/dynamo/musica/rss2.xml', 'http://g1.globo.com/dynamo/natureza/rss2.xml', 'http://g1.globo.com/dynamo/planeta-bizarro/rss2.xml', 'http://g1.globo.com/dynamo/politica/mensalao/rss2.xml', 'http://g1.globo.com/dynamo/pop-arte/rss2.xml', 'http://g1.globo.com/dynamo/tecnologia/rss2.xml', 'http://g1.globo.com/dynamo/turismo-e-viagem/rss2.xml']
last_news = []                       #

def read_news():
    for URL in FEEDS_URL:
        NewsFeed = feedparser.parse(URL)

        last_news.clear()
        for entry in NewsFeed.entries:
            # salvar ultimas noticias
            last_news.append({'title': entry.title, 'link': entry.link})

            # inserir noticia no banco de dados
            db.insert_news(entry.title, entry.summary)

def get_last_news():
    return last_news