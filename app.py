import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, render_template, request, session, redirect, url_for
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


@app.route("/")
def hello():
    return render_template('accueil.html')


@app.route("/publier")
def publier():
    return render_template('publier.html')


@app.route("/inscription")
def index():
    return render_template('inscription.html')


@app.route("/connexion")
def connect():
    return render_template('connexion.html')


@app.route('/tentative_connexion', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'adresse_courriel' in request.form and 'mot_de_passe' in request.form:
        adresse_courriel = request.form['adresse_courriel']
        mot_de_passe = request.form['mot_de_passe']
        cursor = mysql.cursor(cursor=DictCursor)
        cursor.execute(
            'SELECT * FROM utilisateurs WHERE adresse_courriel = %s AND mot_de_passe = %s',
            (adresse_courriel, mot_de_passe,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['adresse_courriel']
            print(session['loggedin'])
            return 'Logged in successfully!'
        else:
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
        (prenom, nom, adresse_courriel, mot_de_passe, num_tel, adresse_civique)
    )

    mysql.commit()
    mysql.cursor().close()

    return render_template('accueil.html')


@app.route('/recherche', methods=['GET', 'POST'])
def recherche():
    if request.method == 'POST':
        recherche = request.form.get('mot_cle')
        query = "SELECT * FROM Annonces WHERE titre_annonce LIKE %s"
        cursor = mysql.cursor(cursor=DictCursor)
        cursor.execute(query, ('%' + recherche + '%',))
        annonces = cursor.fetchall()
        return render_template('resultats.html', annonces=annonces)
    return render_template('resultats.html')




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


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
