import pymysql
from flask import Flask, request
from flask import render_template

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Toshib@123'
app.config['MYSQL_DB'] = 'flask_crud'

mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)


def create_table():
    try:
        print('Creating Table Started =====')
        cur = mysql.cursor()
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY ,
                name VARCHAR(255) NOT NULL,
                description TEXT
            )
            '''
        )
        mysql.commit()
        cur.close()
        print('Items Table Created =====')
    except Exception as e:
        print("Error while creating table", e)


@app.route("/")
def hello():
    return render_template('accueil.html')


@app.route("/inscription")
def index():
    return render_template('inscription.html')


@app.route("/ProchainePage", methods=['POST'])
def ProchainePage():
    prenom = request.form.get('prenom')
    nom = request.form.get('nom')
    email = request.form.get('courriel')
    password = request.form.get('mot-de-passe')

    mysql.cursor().execute(
        'INSERT INTO users (email, password) VALUES (%s, %s)', (email, password)

    )
    mysql.commit()
    mysql.cursor().close()

    return render_template('Page2.html')


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
