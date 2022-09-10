import sqlite3
import services.dictionary as dictionary

conn = sqlite3.connect('database/feed.db', check_same_thread=False)
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
                content TEXT
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
                tag TEXT
            );
        """)
        print("Tabela de tags criada com sucesso!")

def get_connection():
    return conn

def close_connection():
  conn.close()

def insert_news(title, content):
    cursor.execute("""SELECT id FROM news WHERE title = ?;""", (title,))
    if cursor.fetchone() is None:
        print('Inserindo notícia de título {}'.format(title))
        cursor.execute("""INSERT INTO news (title, content) VALUES (?, ?);""", (title, content))
        conn.commit()
        print("Notícia inserida com sucesso!")

        # salvar tags
        cursor.execute("""SELECT id FROM news WHERE title = ?;""", (title,))
        news_id = cursor.fetchone()[0]
        filtred = dictionary.suit_text(title + " " + content)
        array_word_occurrence = dictionary.word_count(filtred[0])
        insert_tags(news_id, array_word_occurrence)
        

def insert_tags(news_id, tags):
    for tag in tags:
        cursor.execute("""SELECT id FROM tags WHERE news_id = ? AND tag = ?;""", (news_id, tag))
        if cursor.fetchone() is None:
            cursor.execute("""INSERT INTO tags (news_id, tag) VALUES (?, ?);""", (news_id, tag))
            conn.commit()

def insert_user(username, password):
    cursor.execute("""SELECT id FROM users WHERE username = ?;""", (username,))
    if cursor.fetchone() is None:
        print('Inserindo usuário de nome {}'.format(username))
        cursor.execute("""INSERT INTO users (username, password) VALUES (?, ?);""", (username, password))
        conn.commit()
        print("Usuário inserido com sucesso!")

        cursor.execute("""SELECT id FROM users WHERE username = ?;""", (username,))
        user_id = cursor.fetchone()[0]
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

def insert_preference(user_id, title):
    cursor.execute("""SELECT id FROM news WHERE title = ?;""", (title,))
    news_id = cursor.fetchone()[0]
    
    print('Inserindo preferência de usuário {} para notícia {}'.format(user_id, news_id))
    cursor.execute("""INSERT INTO preferences (user_id, news_id) VALUES (?, ?);""", (user_id, news_id))
    conn.commit()
    print("Preferência inserida com sucesso!")