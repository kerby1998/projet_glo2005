import pymysql
from pymysql.cursors import DictCursor

from flask import Flask, render_template, request, redirect, url_for, session
from flask import render_template
import hashlib


app = Flask(__name__)

app.secret_key = 'roberto'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Toshib@123'
app.config['MYSQL_DB'] = 'livremarketbd'

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


@app.route("/connexion")
def connect():
    return render_template('connexion.html')


@app.route('/tentative_connexion', methods=['GET', 'POST'])
def login():
    # Output a message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        addresse_courriel = request.form['username']
        mot_de_passe = request.form['password']
        # Check if account exists using MySQL
        mysql.cursor().execute('SELECT * FROM utilisateurs WHERE adresse_courriel = %s AND mot_de_passe = %s', (addresse_courriel, mot_de_passe,))
        # Fetch one record and return result
        account = mysql.cursor().fetchone
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('accueil.html', msg=msg)

@app.route("/ProchainePage", methods=['POST', 'GET'])
def ProchainePage():
    prenom = request.form.get('prenom')
    nom = request.form.get('nom')
    adresse_courriel = request.form.get('adresse_courriel')
    mot_de_passe = request.form.get('mot_de_passe')
    num_tel = request.form.get('num_tel')
    adresse_civique = request.form.get('adresse_civique')

    hash = mot_de_passe + app.secret_key
    hash = hashlib.sha1(hash.encode())
    mot_de_passe = hash.hexdigest()

    # Execute database insertion
    mysql.cursor().execute(
        "INSERT INTO `utilisateurs` (prenom,nom,`adresse_courriel`, `mot_de_passe`, `num_tel`, `adresse_civique`) VALUES (%s,%s, %s, %s, %s, %s)",
        (prenom,nom, adresse_courriel, mot_de_passe, num_tel, adresse_civique)
    )

    mysql.commit()
    mysql.cursor().close()

    return render_template('accueil.html')

@app.route('/annonce/<int:id_annonce>')
def retourner_colonne(id_annonce):
    cursor = mysql.cursor(cursor=DictCursor)
    cursor.execute("SELECT * FROM annonces WHERE id_annonce = %s", (id_annonce,))
    annonces = cursor.fetchone()
    print(annonces)
    if annonces:
        return render_template('detail.html', annonce=annonces)
    else:
        return "Aucune annonce trouvée avec cet ID"


if __name__ == '__main__':
    create_table()
    app.run()
