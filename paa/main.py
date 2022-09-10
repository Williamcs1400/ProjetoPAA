from re import template
from flask import Flask, render_template, request
import database.database_operations as db
import services.read_xml as read_xml

app = Flask(__name__)

db_connection = None
current_user = None

# opreacoes iniciais do app
def init_app():
    print('Iniciando aplicação...')
    db.create_tables()
    db_connection = db.get_connection()
    read_xml.read_news()

# pagina raiz
@app.route('/')
def main():
    return render_template('login.html')

@app.route('/click_news', methods=['POST'])
def click_news():
    title = request.values.get('title')
    
    db.insert_preference(current_user, title)
    return render_template('news.html', data=read_xml.get_last_news())

@app.route('/register', methods=['POST'])
def register():
    name =  request.form['name_register']
    username = request.form['username_register']
    password = request.form['password_register']

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

    result = db.compare_user(username,password)

    if result[0] == True:
        current_user = result[1]
        print('current_user: ', current_user)
        return render_template('news.html', data=read_xml.get_last_news())
    else:
        return render_template('login.html')

@app.route("/to_register")
def to_register():
    return render_template('register.html')

@app.route("/to_login")
def to_login():
    return render_template('login.html')

if __name__ == '__main__':
    init_app()

app.run(debug=True) # tirar o debug=True quando for apresentar