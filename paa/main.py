from flask import Flask, render_template
import database.database_operations as db
import services.read_xml as read_xml

app = Flask(__name__)

db_connection = None

@app.route('/')
def main():
    db.create_tables()
    db_connection = db.get_connection()
    read_xml.read_news()
    return render_template('login.html')

@app.route("/login/", methods=['POST'])
def move_forward():
    # db.insert_user('username', 'password')
    return render_template('index.html')

app.run(debug=True) # tirar o debug=True quando for apresentar