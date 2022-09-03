from re import template
from flask import Flask, render_template, request
import database.database_operations as db
import services.read_xml as read_xml


app = Flask(__name__)

db_connection = None

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

@app.route('/register', methods=['POST'])
def register():
    name =  request.form['name_register']
    username = request.form['password_register']
    password = request.form['username_register']

    print('name: ', name)
    print('username: ', username)
    print('password: ', password)

    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # fazer login
    return render_template('index.html')

@app.route("/to_register")
def to_register():
    return render_template('register.html')

@app.route("/to_login")
def to_login():
    return render_template('login.html')

if __name__ == '__main__':
    init_app()

app.run(debug=True) # tirar o debug=True quando for apresentar