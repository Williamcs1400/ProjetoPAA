import sqlite3
import services.dictionary as dictionary

conn = sqlite3.connect('database/feed.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def create_tables():
    # verificar se tabela users existe
    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name='users';""")
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
    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name='preferences';""")
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
    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name='news';""")
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
    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name='tags';""")
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

    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name='user_tags';""")
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
        cursor.execute(
            """INSERT INTO news (title, content, link) VALUES (?, ?, ?);""", (title, content, link))
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
        print('Inserindo tag {} com peso {} para notícia {}'.format(
            tag, weight, news_id))
        cursor.execute(
            """SELECT id FROM tags WHERE news_id = ? AND tag = ?;""", (news_id, tag))
        if cursor.fetchone() is None:
            cursor.execute(
                """INSERT INTO tags (news_id, tag, weight) VALUES (?, ?, ?);""", (news_id, tag, weight))
            conn.commit()


def insert_user(username, password):
    cursor.execute("""SELECT id FROM users WHERE username = ?;""", (username,))
    if cursor.fetchone() is None:
        print('Inserindo usuário de nome {}'.format(username))
        cursor.execute(
            """INSERT INTO users (username, password) VALUES (?, ?);""", (username, password))
        conn.commit()
        print("Usuário inserido com sucesso!")

        cursor.execute(
            """SELECT id FROM users WHERE username = ?;""", (username,))
        user_id = cursor.fetchone()['id']
        return (True, user_id)

    else:
        print("Usuário já existe!")
        return (False, "")


def compare_user(username, password):

    cursor.execute(
        """SELECT id FROM users WHERE username = ? AND password = ?;""", (username, password))
    result = cursor.fetchone()
    if result is None:
        return (False, -1)
    else:
        return (True, str(result[0]))


def insert_user_tags(user_id, tags):

    for tag in tags:

        cursor.execute(
            """SELECT count FROM user_tags WHERE user_id = ? AND tag = ?;""", (user_id, tag))
        count = cursor.fetchone()

        if cursor.fetchone() is None:
            print('Inserindo tag {} para usuário {}'.format(tag, user_id))
            cursor.execute(
                """INSERT INTO user_tags (user_id, tag, count) VALUES (?, ?, ?);""", (user_id, tag, 1))
            conn.commit()
        else:
            count = count['count']
            print('Atualizando tag {} para usuário {} com count {}'.format(
                tag, user_id, count))
            cursor.execute(
                """UPDATE user_tags SET count = ? WHERE user_id = ? AND tag = ?;""", (count+1, user_id, tag))
            conn.commit()


def insert_preference(user_id, title):
    cursor.execute("""SELECT id FROM news WHERE title = ?;""", (title,))
    news_id = cursor.fetchone()['id']

    print('Inserindo preferência de usuário {} para notícia {}'.format(user_id, news_id))
    cursor.execute(
        """INSERT INTO preferences (user_id, news_id) VALUES (?, ?);""", (user_id, news_id))
    conn.commit()
    print("Preferência inserida com sucesso!")

    # SELECIONA TODAS AS TAGS DA NOTÍCIA
    cursor.execute(
        """SELECT news_id, tag, weight FROM tags WHERE news_id = ?;""", (str(news_id),))
    tags = cursor.fetchall()

    # LISTA DE TAGS E RESPECTIVO PESO =>  [(tag1, peso1), (tag2, peso2), ...]
    tags_list = [t['tag'] for t in tags[:10]]
    weights_list = [round(t['weight'], 5) for t in tags[:10]]
    tags = list(zip(tags_list, weights_list))

    # ORDENA PELO PESO
    tags.sort(key=lambda x: x[1], reverse=True)
    tags = [t[0] for t in tags]

    # print(tags)

    insert_user_tags(user_id, tags)


def get_news_paginated(user_id, page=1):
    updated_conn = sqlite3.connect('database/feed.db', check_same_thread=False)
    updated_conn.row_factory = sqlite3.Row
    updated_cursor = conn.cursor()

    news_list = get_preferred_news(user_id, page, 20)
    print(news_list)
    updated_cursor.execute(news_list)
    #updated_cursor.execute(
    #    """SELECT * FROM news order by id desc limit ? offset ?;""", (20, 20*(page-1)))
    news = updated_cursor.fetchall()

    formated_news = []
    if news is not None:
        for item in news:
            formated_news.append(
                {'title': item['title'], 'link': item['link'], 'content': item['content']})

    return formated_news


def get_preferred_news(user_id, page, page_size):
    cursor.execute("SELECT COUNT(id) FROM news;")
    news_list_size = cursor.fetchone()[0]
    news_list = [[0]*2 for _ in range(news_list_size)]

    # Gera uma lista de noticias associadas a um peso de preferencia do usuario
    for i in range(news_list_size):
        news_list[i][0] = i+1
        cursor.execute("SELECT tag,weight FROM tags WHERE news_id = ?;", [i+1])
        tags = cursor.fetchall()
        cursor.execute("SELECT tag,count FROM user_tags WHERE user_id = ?;", (user_id))
        user_tags = cursor.fetchall()
        for j in tags:
            for k in user_tags:
                if j[0] == k[0]:
                    news_list[i][1] = news_list[i][1]+(j[1] * k[1])

    # Ordena a lista com base no maior peso, e secundariamente com base nas noticias mais recentes
    news_list.sort(key=lambda x:x[0], reverse=True)
    news_list.sort(key=lambda x:x[1], reverse=True)

    # Gera a string com a lista de noticias para o comando SQL
    limits = check_page(page, page_size, news_list_size)

    news_list_string = "SELECT * FROM news WHERE id IN ("
    for i in range(limits[0],limits[1]):
        news_list_string += str(news_list[i][0]) + ", "
    news_list_string += str(news_list[limits[1]][0]) + ")"
    #news_list_string += ";"

    news_list_string += " ORDER BY CASE "
    for i in range(limits[0],limits[1]):
        news_list_string += "WHEN id = " + str(news_list[i][0]) + " THEN " + str(i) + " "
    news_list_string += "WHEN id = " + str(news_list[limits[1]][0]) + " THEN " + str(limits[1]) + " END, id"
    news_list_string += ";"

    return news_list_string


def check_page(page, page_size, news_list_size):
    if (page-1)*page_size >= news_list_size:
        return check_page(page-1, page_size, news_list_size)
    elif page*page_size > news_list_size:
        return [(page-1)*page_size if (page > 1) else 1, news_list_size-1]
    else:
        return [(page-1)*page_size if (page > 1) else 1, page*page_size-1]
