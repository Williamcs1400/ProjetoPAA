import sqlite3
import services.dictionary as dictionary

conn = sqlite3.connect('database/feed.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def create_tables():
    # verificar se tabela users existe
    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='users';""")
    if cursor.fetchone() is None:
        print("Criando tabela de usuários...")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT
            );
        """)
        print("Tabela de usuários criada com sucesso!")

    # verificar se tabela preferences existe
    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='preferences';""")
    if cursor.fetchone() is None:
        print("Criando tabela de preferências...")
        cursor.execute("""
            CREATE TABLE preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                news_id INTEGER
            );
        """)
        print("Tabela de preferências criada com sucesso!")

    # verificar se tabela news existe
    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='news';""")
    if cursor.fetchone() is None:
        print("Criando tabela de notícias...")
        cursor.execute("""
            CREATE TABLE news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                link TEXT
            );
        """)
        print("Tabela de notícias criada com sucesso!")

    # verificar se tabela tags existe
    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='tags';""")
    if cursor.fetchone() is None:
        print("Criando tabela de tags...")
        cursor.execute("""
            CREATE TABLE tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER,
                tag TEXT,
                weight REAL
            );
        """)
        print("Tabela de tags criada com sucesso!")


    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='user_tags';""")
    if cursor.fetchone() is None:
        print("Criando tabela de tags de usuário...")
        cursor.execute("""
            CREATE TABLE user_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tag TEXT,
                count INTEGER
            );
        """)
        print("Tabela de tags de usuário criada com sucesso!")

def get_connection():
    return conn

def close_connection():
  conn.close()

def insert_news(title, content, link):
    cursor.execute("""SELECT id FROM news WHERE title = ?;""", (title,))
    if cursor.fetchone() is None:
        print('Inserindo notícia de título {}'.format(title))
        cursor.execute("""INSERT INTO news (title, content, link) VALUES (?, ?, ?);""", (title, content, link))
        conn.commit()
        print("Notícia inserida com sucesso!")

        # salvar tags
        cursor.execute("""SELECT id FROM news WHERE title = ?;""", (title,))
        news_id = cursor.fetchone()['id']
        filtered_text = dictionary.suit_text(title + " " + content)
        tags_with_weight = dictionary.get_tags_weight(filtered_text)
        insert_tags(news_id, tags_with_weight)
        

def insert_tags(news_id, tags):
    for tag, weight in tags.items():
        print('Inserindo tag {} com peso {} para notícia {}'.format(tag, weight, news_id))
        cursor.execute("""SELECT id FROM tags WHERE news_id = ? AND tag = ?;""", (news_id, tag))
        if cursor.fetchone() is None:
            cursor.execute("""INSERT INTO tags (news_id, tag, weight) VALUES (?, ?, ?);""", (news_id, tag, weight))
            conn.commit()

def insert_user(username, password):
    cursor.execute("""SELECT id FROM users WHERE username = ?;""", (username,))
    if cursor.fetchone() is None:
        print('Inserindo usuário de nome {}'.format(username))
        cursor.execute("""INSERT INTO users (username, password) VALUES (?, ?);""", (username, password))
        conn.commit()
        print("Usuário inserido com sucesso!")

        cursor.execute("""SELECT id FROM users WHERE username = ?;""", (username,))
        user_id = cursor.fetchone()['id']
        return (True, user_id)

    else:
        print("Usuário já existe!")
        return (False, "")

def compare_user(username, password):

    cursor.execute("""SELECT id FROM users WHERE username = ? AND password = ?;""", (username, password))
    result = cursor.fetchone()
    if result is None:
        return (False, -1)
    else:
        return (True, str(result[0]))

def insert_user_tags(user_id, tags):

    for tag, count in tags.items():
        print('Inserindo tag {} com contagem {} para usuário {}'.format(tag, count, user_id))

        cursor.execute("""SELECT id FROM user_tags WHERE user_id = ? AND tag = ?;""", (user_id, tag))

        if cursor.fetchone() is None:
            cursor.execute("""INSERT INTO user_tags (user_id, tag, count) VALUES (?, ?, ?);""", (user_id, tag, count))
            conn.commit()
        else:
            cursor.execute("""UPDATE user_tags SET count = ? WHERE user_id = ? AND tag = ?;""", (count, user_id, tag))
            conn.commit()




def insert_preference(user_id, title):
    cursor.execute("""SELECT id FROM news WHERE title = ?;""", (title,))
    news_id = cursor.fetchone()['id']
    
    print('Inserindo preferência de usuário {} para notícia {}'.format(user_id, news_id))
    cursor.execute("""INSERT INTO preferences (user_id, news_id) VALUES (?, ?);""", (user_id, news_id))
    conn.commit()
    print("Preferência inserida com sucesso!")
    
    # SELECIONA TODAS AS TAGS DA NOTÍCIA
    cursor.execute("""SELECT news_id, tag, weight FROM tags WHERE news_id = ?;""", (str(news_id),))
    tags = cursor.fetchall()

    # LISTA DE TAGS E RESPECTIVO PESO =>  [(tag1, peso1), (tag2, peso2), ...]
    tags_list = [t['tag'] for t in tags]
    weights_list = [round(t['weight'], 5) for t in tags]

    tags = list(zip(tags_list, weights_list))

    tags.sort(key=lambda x: x[1], reverse=True)
    tags = tags[:10]


def get_news_paginated():
    updated_conn = sqlite3.connect('database/feed.db', check_same_thread=False)
    updated_conn.row_factory = sqlite3.Row
    updated_cursor = conn.cursor()

    updated_cursor.execute("""SELECT * FROM news order by id desc limit ? offset ?;""", (20, 0))
    news = updated_cursor.fetchall()

    # print(news)

    formated_news = []
    if news is not None:
        for item in news:
            formated_news.append({'title': item['title'], 'link': item['link'], 'content': item['content']})

    return formated_news