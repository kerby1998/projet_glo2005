import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, render_template, request, session, redirect, url_for
import hashlib

from Requêtes import *
import os
import bcrypt

secret_key = os.urandom(24)

app = Flask(__name__)

app.secret_key = secret_key

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'livremarketbd'

mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

#cursor = mysql.cursor(cursor=DictCursor)
cursor = mysql.cursor()


@app.route("/")
def pageAccueil():
    return render_template('accueil.html')


@app.route("/publier")
def pagePublier():
    try:
        if 'adresse_courriel' in session:
            return render_template('publier.html')
        else:
            return render_template("connexion.html")
    except Exception as e:
        return f"Une erreur s'est produite lors de la tentative de publication : {str(e)}"


@app.route("/inscription")
def inscription():
    return render_template('inscription.html')


@app.route("/faq")
def faq():
    return render_template('faq.html')


@app.route("/mon_panier")
def mon_panier():
    return render_template('panier.html')


@app.route("/inscription")
def pageInscription():
    return render_template('inscription.html')


@app.route("/connexion")
def pageConnexion():
    return render_template('connexion.html')


@app.route('/connexion_compte', methods=['POST'])
def connexion_au_compte():
    # Connexion au compte d'un utilisateur existant

        adresse_courriel = request.form['adresse_courriel']
        mot_de_passe = request.form['mot_de_passe']

        cursor.execute("SELECT mot_de_passe FROM Utilisateurs WHERE adresse_courriel = %s", (adresse_courriel,))
        result = cursor.fetchone()
        print(result)

        if result:
            mot_de_passe_chiffre = result[0]
            print("mot de passe", mot_de_passe_chiffre)

            if bcrypt.checkpw(mot_de_passe.encode('utf-8'), mot_de_passe_chiffre.encode('utf-8')):
                session['adresse_courriel'] = adresse_courriel
                cursor.execute(
                    "SELECT adresse_courriel,prenom,nom,adresse_civique,num_tel FROM Utilisateurs WHERE adresse_courriel = %s",
                    (adresse_courriel,))
                result2 = cursor.fetchone()
                return render_template('compte.html', informations_compte=result2)
            else:
                return 'Adresse courriel ou mot de passe invalide.'

        else:
            return 'Adresse courriel ou mot de passe invalide.'

def chiffrer_mot_de_passe(mot_de_passe):
    return bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())


@app.route('/inscription', methods=['POST'])
def create_account():
    # Création d'un compte pour un nouvel utilisateur

        prenom = request.form.get('prenom')
        nom = request.form.get('nom')
        adresse_courriel = request.form.get('adresse_courriel')
        mot_de_passe = request.form.get('mot_de_passe')
        adresse_civique = request.form.get('adresse_civique')
        num_tel = request.form.get('num_tel')

        mot_de_passe_chiffre = chiffrer_mot_de_passe(mot_de_passe)
        print("longueur:", len(mot_de_passe_chiffre))
        print("mot de passe :", mot_de_passe)
        print("mot de passe chiffré:", mot_de_passe_chiffre)

        cursor = mysql.cursor()

        cursor.execute(
            'INSERT INTO Utilisateurs (adresse_courriel, prenom, nom, mot_de_passe, adresse_civique, num_tel) VALUES (%s, %s, %s, %s, %s, %s)',
            (adresse_courriel, prenom, nom, mot_de_passe_chiffre, adresse_civique, num_tel)

        )
        mysql.commit()
        cursor.close()

        return render_template('connexion.html', message = "Votre compte a été créé avec succès. Veuillez vous connecter.")




@app.route('/recherche', methods=['GET', 'POST'])
def rechercherAnnonces():
    if request.method == 'POST':
        args = []
        titre = request.form.get('titre_annonce')
        genre = request.form.get('genre')
        etat = request.form.get('etat')
        statut = request.form.get('statut')
        prix_min = request.form.get('prix_min')
        prix_max = request.form.get('prix_max')


        query = "SELECT * FROM Annonces WHERE 1"


        print(titre)

        if genre:
            query += " AND genre = %s"
            args.append(genre)

        if titre:
            titre_recherche = f"%{titre}%"
            query += " AND titre_annonce LIKE %s"
            args.append(titre_recherche)

        if etat:
            query += " AND etat = %s"
            args.append(etat)

        if statut:
            query += " AND statut = %s"
            args.append(statut)

        if prix_min:
            query += " AND prix >= %s"
            args.append(prix_min)

        if prix_max:
            query += " AND prix <= %s"
            args.append(prix_max)

        with mysql.cursor(cursor=DictCursor) as cursor:
            cursor.execute(query, args)
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
        return render_template('unique.html', annonce=annonces)
    else:
        return "Aucune annonce trouvée avec cet ID"


@app.route('/mon_compte', methods=['GET'])
def mon_compte():
    try:
        # Vérification si l'utilisateur est connecté
        if 'adresse_courriel' in session:
            # Récupération des informations de compte de l'utilisateur depuis la session
            adresse_courriel = session['adresse_courriel']
            cursor.execute(
                "SELECT adresse_courriel,prenom,nom,adresse_civique,num_tel FROM Utilisateurs WHERE adresse_courriel = %s",
                (adresse_courriel,))
            result = cursor.fetchone()
            return render_template('compte.html', informations_compte=result)
        else:
            return render_template("connexion.html")

    except Exception as e:
        return f"Une erreur s'est produite lors de la récupération des informations de compte : {str(e)}"


@app.route('/panier', methods=['GET'])
def details_panier():
    try:
        if 'adresse_courriel' in session:
            adresse_courriel = session['adresse_courriel']
            # Sélectionner les détails des annonces dans le panier de l'utilisateur
            request = """
            SELECT annonces.titre_annonce, annonces.prix, annonces.id_annonce, panier.id_panier
            FROM PanierAnnonce 
            JOIN annonces ON PanierAnnonce.annonce = annonces.id_annonce 
            JOIN panier ON PanierAnnonce.panier = panier.id_panier
            WHERE panier = (
                SELECT id_panier 
                FROM Panier 
                WHERE adresse_utilisateur = '{}'
            )
            """.format(adresse_courriel)

            cursor.execute(request)
            details_panier = cursor.fetchall()

            # Rendre le template HTML et passer les détails du panier
            return render_template('panier.html', details_panier=details_panier)
        else:
            # Gérer le cas où l'utilisateur n'est pas connecté
            # Redirection vers une page de connexion ou un message d'erreur
            return render_template('connexion.html')  # Exemple de redirection vers une page de connexion
    except Exception as e:
        return f"Une erreur s'est produite lors du chargement du panier : {str(e)}"


@app.route('/historique_achats', methods=['GET'])
def historique_achats():
    try:
        if 'adresse_courriel' in session:
            adresse_courriel = session['adresse_courriel']
            # Sélectionner les détails des achats dans la table transaction
            request = """
            SELECT transactions.date, transactions.montant, annonces.titre_annonce
            FROM transactions 
            JOIN annonces ON transactions.id_annonce = annonces.id_annonce 
            WHERE id_historique = (
                SELECT id_historique
                FROM historiques_transactions 
                WHERE adresse_utilisateur = '{}'
            )
            """.format(adresse_courriel)

            cursor.execute(request)
            historique_achats = cursor.fetchall()

            # Rendre le template HTML et passer les détails du panier
            return render_template('historique_achat.html', historique_achats=historique_achats)
        else:
            # Gérer le cas où l'utilisateur n'est pas connecté
            # Redirection vers une page de connexion ou un message d'erreur
            return render_template('connexion.html')  # Exemple de redirection vers une page de connexion
    except Exception as e:
        return f"Une erreur s'est produite lors du chargement du panier : {str(e)}"


@app.route("/annonce")
@app.route("/annonce/mot-cle/")
def annonce():
    annonces = select_all_annonce()
    return render_template("annonce(mise_en_page).html", annonces=annonces)


@app.route("/annonce/<genre>")
def annonce_par_genre(genre):
    liste_genre = genre.split(",")
    annonces = select_genre_annonce(liste_genre)
    return render_template("annonce(mise_en_page).html", annonces=annonces)


@app.route("/annonce/mot-cle/<mot_cle>")
def recherche(mot_cle):
    annonces = recherche_annonce(mot_cle)
    return render_template("annonce(mise_en_page).html", annonces=annonces)


@app.route('/annonces', methods=['GET'])
def filter_annonces():
    adresse_vendeur = request.args.get('adresse_vendeur')
    etat = request.args.get('etat')
    genre = request.args.get('genre')
    query = "SELECT * FROM Annonces WHERE 1"
    if adresse_vendeur:
        query += " AND adresse_vendeur = '{}'".format(adresse_vendeur)
    if etat:
        query += " AND etat = '{}'".format(etat)
    if genre:
        query += " AND genre = '{}'".format(genre)

    cursor.execute(query)
    annonces = cursor.fetchall()
    return jsonify(annonces)


@app.route('/favoris', methods=['GET'])
def select_details_favoris_utilisateur():
    try:
        if 'adresse_courriel' in session:
            adresse_courriel = session['adresse_courriel']
            # Sélectionner les détails des annonces dans la liste des favoris de l'utilisateur
            request = """
            SELECT annonces.titre_annonce, annonces.id_annonce, panier.id_panier, listes_souhaits.id_souhaits
            FROM contenu_liste_souhaits 
            JOIN Annonces ON contenu_liste_souhaits.id_annonce = Annonces.id_annonce
            JOIN listes_souhaits ON contenu_liste_souhaits.id_liste = listes_souhaits.id_souhaits
            JOIN panier ON listes_souhaits.adresse_utilisateur = panier.adresse_utilisateur
            WHERE id_liste = (
                SELECT id_souhaits 
                FROM listes_souhaits 
                WHERE adresse_utilisateur = '{}'
            )
            """.format(adresse_courriel)

            cursor.execute(request)
            details_favoris = cursor.fetchall()

            return render_template('favoris.html', details_favoris=details_favoris)
        else:
            # Gérer le cas où l'utilisateur n'est pas connecté
            # Redirection vers une page de connexion ou un message d'erreur
            return render_template('connexion.html')
    except Exception as e:
        return f"Une erreur s'est produite lors du chargement du panier : {str(e)}"


@app.route('/ajouter_favoris_panier', methods=['POST'])
def ajouter_annonce_panier():
    try:
        id_panier = request.form['id_panier']
        id_annonce = request.form['id_annonce']
        id_liste = request.form['id_liste']
        query = """INSERT INTO PanierAnnonce (panier, annonce) VALUES ("{}","{}")""".format(id_panier,
                                                                                            id_annonce)

        cursor.execute(query)
        db_connection.commit()

        # Retirer l'annonce de la liste de souhaits
        query_souhaits = """DELETE FROM contenu_liste_souhaits WHERE id_annonce = {} AND id_liste = {}""".format(
            id_annonce, id_liste)
        cursor.execute(query_souhaits)
        db_connection.commit()

        return render_template('favoris.html')
    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout de l'annonce au panier : {str(e)}"


@app.route('/publier_annonce', methods=['POST'])
def publier_annonce():
    if 'adresse_courriel' in session:
        titre_annonce = request.form['titre_annonce']
        adresse_vendeur = session['adresse_courriel']
        description = request.form['description']
        etat = request.form['etat']
        genre = request.form['genre']
        prix = request.form['prix']
        images = request.files.getlist('images')

        connection = mysql
        cursor = connection.cursor()

        # Exécution de la requête SQL pour insérer l'annonce dans la base de données
        query = "INSERT INTO annonces (titre_annonce, description, etat, genre, prix, adresse_vendeur) VALUES (%s,%s, %s, %s, %s, %s)"
        cursor.execute(query, (titre_annonce, description, etat, genre, prix,adresse_vendeur))
        connection.commit()

        # Fermeture de la connexion à la base de données
        cursor.close()
        connection.close()

        return render_template('accueil.html')

@app.route('/supprimer_favoris_panier', methods=['POST'])
def supprimer_favoris_panier():
    try:
        id_annonce = request.form['id_annonce']
        id_liste = request.form['id_liste']
        # Retirer l'annonce de la liste de souhaits
        query_souhaits = """DELETE FROM contenu_liste_souhaits WHERE id_annonce = {} AND id_liste = {}""".format(
            id_annonce, id_liste)
        cursor.execute(query_souhaits)
        db_connection.commit()

        return render_template('favoris.html')
    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout de l'annonce au panier : {str(e)}"


@app.route('/supprimer_annonce_panier', methods=['POST'])
def supprimer_annonce_panier():
    try:
        id_panier = request.form['id_panier']
        id_annonce = request.form['id_annonce']

        query = """DELETE FROM PanierAnnonce WHERE annonce = {} AND panier = {}""".format(id_annonce, id_panier)

        cursor.execute(query)
        db_connection.commit()

        return render_template('panier.html')
    except Exception as e:
        return f"Une erreur s'est produite lors de la suppression de l'annonce du panier : {str(e)}"


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('courriel', None)
    return redirect(url_for('pageConnexion'))


if __name__ == '__main__':
    app.run()
