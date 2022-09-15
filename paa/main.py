from re import template
from flask import Flask, render_template, request, redirect, session, flash
import database.database_operations as db
from services import read_xml
from services import security
import threading

INTERVAL = 60                        # tempo de intervalo entre as chamadas leituras do feed

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
db_connection = None

# operacoes iniciais do app
def init_app():
    print('Iniciando aplicação...')
    db.create_tables()
    threading.Timer(INTERVAL, read_xml.read_news).start()

# pagina raiz
@app.route('/')
def main():
    session['user_id'] = 0
    return render_template('login.html')

@app.route('/click_news', methods=['POST'])
def click_news():
    title = request.values.get('title')

    db.insert_preference(session['user_id'], title)
    return render_template('news.html', data=db.get_news_paginated())

@app.route('/register', methods=['POST'])
def register():
    name =  request.form['name_register']
    username = request.form['username_register']
    password = request.form['password_register']

    if name == '':
        flash("Informe seu nome")
    if username == '':
        flash("Informe seu usuario")
    if password == '':
        flash("Informe sua senha")


    password = security.hash_sha256(password)

    db.insert_user(username, password)

    print('name: ', name)
    print('username: ', username)
    print('password: ', password)

    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # fazer login
    username = request.form['username_login']
    password = request.form['password_login']

    if username == '':
        flash("Informe seu usuario")
    if password == '':
        flash("Informe sua senha")

    password = security.hash_sha256(password)

    result = db.compare_user(username,password)

    if result[0] == True:
        session['user_id'] = result[1]
        print('current_user: ', session['user_id'])
        return redirect('/news')
    else:
        flash("Usuario ou senha incorretos")
        return render_template('login.html')

@app.route('/news')
def news():
    if session['user_id'] == 0:
        return redirect("/")
    else:
        return render_template('news.html', data=db.get_news_paginated())

@app.route('/logout')
def logout():
    session['user_id'] = 0
    return redirect("/")

@app.route("/to_register")
def to_register():
    return render_template('register.html')

@app.route("/to_login")
def to_login():
    return render_template('login.html')

if __name__ == '__main__':
    init_app()

app.run(debug=True) # tirar o debug=True quando for apresentar
