from flask import Flask, request, render_template, session, jsonify
from app import cursor
#import mysql.connector
import bcrypt
import os
import pymysql

app = Flask(__name__)
db_connection = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="LivreMarketBD"
)

cursor = db_connection.cursor()


def chiffrer_mot_de_passe(mot_de_passe):
    return bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())


@app.route('/create_account', methods=['POST'])
def create_account():
    # Création d'un compte pour un nouvel utilisateur
    try:
        adresse_courriel = request.form['adresse_courriel']
        prenom = request.form['prenom']
        nom = request.form['nom']
        mot_de_passe = request.form['mot_de_passe']

        mot_de_passe_chiffre = chiffrer_mot_de_passe(mot_de_passe)

        query = ("INSERT INTO Utilisateurs (adresse_courriel, prenom, nom, mot_de_passe)"
                 " VALUES (%s, %s, %s, %s)")
        cursor.execute(query, (adresse_courriel, prenom, nom, mot_de_passe_chiffre))
        db_connection.commit()

        return 'Votre compte utilisateur à été créé avec succès.'

    except Exception as e:
        return f"Une erreur s'est produite lors de la création de votre compte : {str(e)}"


#@app.route('/connexion_compte', methods=['GET'])
def connexion_au_compte():
    # Connexion au compte d'un utilisateur existant
    try:
        adresse_courriel = request.form['adresse_courriel']
        mot_de_passe = request.form['mot_de_passe']

        cursor.execute("SELECT mot_de_passe FROM Utilisateurs WHERE adresse_courriel = %s", (adresse_courriel,))
        result = cursor.fetchone()

        if result:
            mot_de_passe_chiffre = result[0]

            if bcrypt.checkpw(mot_de_passe.encode('utf-8'), mot_de_passe_chiffre):
                session['adresse_courriel'] = adresse_courriel
                return 'Connexion au compte effectuée avec succès.'
            else:
                return 'Adresse courriel ou mot de passe invalide.'

        else:
            return 'Adresse courriel ou mot de passe invalide.'

    except Exception as e:
        return f"Une erreur s'est produite lors de la connexion à votre compte : {str(e)}"


# ROUTE
def enregistrer_infos_utilisateur():
    # Lorsque l'utilisateur passe une commande, il doit entrer ses infos et il a l'option de les enregistrer
    # Lorsqu'il est dans la page client, l'utilisateur à l'option d'entrer ses infos additionnelles
    try:
        adresse = request.form['adresse']
        telephone = request.form['telephone']

        query = "INSERT INTO Utilisateurs (adresse_civique, num_tel) VALUES (%s, %s)"
        cursor.execute(query, (adresse, telephone))

        db_connection.commit()

        return jsonify({'message': 'Informations ajoutées avec succès.'})

    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout de vos informations : {str(e)}"


# ROUTE
def filte_livre():
    # Dans le catalogue de livres, l'utilisateur coche les différentes valeurs d'attributs qu'il veut
    try:
        titre = request.args.get('titre')
        auteur = request.args.get('auteur')
        genre = request.args.get('genre')
        isbn = request.args.get('isbn')
        annee = request.args.get('annee')

        query = "SELECT * FROM Livres WHERE 1=1"
        parametres = []

        if titre:
            query += " AND titre_livre = %s"
            parametres.append(titre)
        if auteur:
            query += " AND auteur = %s"
            parametres.append(auteur)
        if genre:
            # L'utilisateur peut cocher plusieurs genres
            query += " AND genre in = %s" % ','.join(['%s'] * len(genre))
            parametres.append(genre)
        if isbn:
            query += " AND isbn = %s"
            parametres.append(isbn)
        if annee:
            query += " AND annee = %s"
            parametres.append(annee)

        cursor.execute(query, parametres)
        livres = cursor.fetchall()

        return render_template('resultats_filtre_livre.html', livres=livres)

    except Exception as e:
        return f"Une erreur s'est produite lors du filtrage des résultats : {str(e)}"


# ROUTE
def filtre_annonce():
    # Dans la page d'annonces, l'utilisateur coche les différentes valeurs d'attributs qu'il veut
    try:
        titre = request.args.get('titre')
        prix_min = request.args.get('prix_min')
        prix_max = request.args.get('prix_max')
        genre = request.args.get('genre')
        etat = request.args.get('état')

        query = 'SELECT * FROM Annonces WHERE 1=1'
        parametres = []

        if titre:
            query += " AND titre_annonce = %s"
            parametres.append(titre)
        if prix_min:
            query += " AND prix >= %s"
            parametres.append(prix_min)
        if prix_max:
            query += " AND prix <= %s"
            parametres.append(prix_max)
        if genre:
            # l'utilisateur peut cocher plusieurs genres
            query += " AND genre in = %s" % ','.join(['%s'] * len(genre))
            parametres.append(genre)
        if etat:
            query += " AND etat = %s"
            parametres.append(etat)

        cursor.execute(query, parametres)
        annonces = cursor.fetchall()

        return render_template('resultats_filtre_annonce.html', annonces=annonces)

    except Exception as e:
        return f"Une erreur s'est produite lors du filtrage des résultats : {str(e)}"


# ROUTE
def recherche_globale(terme_recherche):
    # Recherche globale de livre ou d'annonce par titre dans la page d'accueil
    try:
        cursor.execute("SELECT * FROM Livres WHERE titre_livre LIKE %s", ('%' + terme_recherche + '%'))
        resultats_livres = cursor.fetchall()

        cursor.execute("SELECT * FROM Livres WHERE titre_livre LIKE %s", ('%' + terme_recherche + '%'))
        resultats_annonces = cursor.fetchall()

        return resultats_livres, resultats_annonces

    except Exception as e:
        return f"Une erreur s'est produite lors de la recherche : {str(e)}"


# ROUTE
def recherche_livre(terme_recherche):
    # Recherche dans la page "Livres"
    try:
        cursor.execute("SELECT * FROM Livres WHERE titre_livre LIKE %s", ('%' + terme_recherche + '%'))
        resultats_livres = cursor.fetchall()

        return resultats_livres

    except Exception as e:
        return f"Une erreur s'est produite lors de la recherche : {str(e)}"


# ROUTE
def recherche_annonce(terme_recherche):
    # Recherche dans la page "Annonces"
    try:
        cursor.execute("SELECT * FROM Annonces WHERE titre_annonce LIKE %s", ('%' + terme_recherche + '%'))
        resultats_annonces = cursor.fetchall()

        return resultats_annonces

    except Exception as e:
        return f"Une erreur s'est produite lors de la recherche : {str(e)}"


# ROUTE
def ajouter_annonce_panier_listesouhaits():
    # Ajouter une annonce à la liste de souhait ou au panier
    try:
        adresse_utilisateur = session['adresse_utilisateur']
        id_element = request.form['id_element']
        destination = request.form['destination']  # Liste ou panier

        if destination == 'Liste de souhaits':
            id_dest_query = "SELECT id_souhaits FROM Listes_Souhaits WHERE adresse_utilisateur = %s"
            cursor.execute(id_dest_query, (adresse_utilisateur,))
            id_dest = cursor.fetchone()[0]
            query = "INSERT INTO Contenu_Liste_Souhaits (id_liste, id_annonce) VALUES (%s, %s)"
            message = "L'élément a été ajouté avec succès à la liste de souhaits."

        elif destination == 'Panier':
            id_dest_query = "SELECT id_panier FROM Panier WHERE adresse_utilisateur = %s"
            cursor.execute(id_dest_query, (adresse_utilisateur,))
            id_dest = cursor.fetchone()[0]
            query = "INSERT INTO Panier (id_panier, adresse_utilisateur) VALUES (%s, %s)"
            message = "L'élément a été ajouté avec succès au panier."

        cursor.execute(query, (id_dest, id_element))
        db_connection.commit()

        return jsonify({'message': message})

    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout de l'élément : {str(e)}"


def ajouter_livre__listesouhaits():
    # Ajouter un livre à la liste de souhait
    try:
        adresse_utilisateur = session['adresse_utilisateur']
        id_element = request.form['id_element']

        id_liste_query = "SELECT id_souhaits FROM Listes_Souhaits WHERE adresse_utilisateur = %s"

        cursor.execute(id_liste_query, (adresse_utilisateur,))
        id_liste = cursor.fetchone()[0]

        query = "INSERT INTO Contenu_Liste_Souhaits (id_liste, id_annonce) VALUES (%s, %s)"

        cursor.execute(query, (id_liste, id_element))
        db_connection.commit()

        return jsonify({'message': "L'élément a été ajouté avec succès à la liste de souhaits."})

    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout de l'élément : {str(e)}"


# ROUTE
def ajouter_une_annonce():
    # L'utilisateur ajoute une annonce
    try:
        titre_annonce = request.form.get('titre_annonce')
        description = request.form.get('description')
        etat = request.form.get('etat')
        genre = request.form.get('genre')
        prix = request.form.get('prix')
        statut = request.form.get('statut')
        adresse_vendeur = session['adresse_utilisateur']
        photos_annonce = request.form.get('url_photos_annonces')

        cursor.execute("START TRANSACTION;")

        cursor.execute("INSERT INTO Annonces (adresse_vendeur, titre_annonce, description, etat, genre, prix, statut) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (adresse_vendeur, titre_annonce, description, etat, genre, prix, statut))

        cursor.execute("SELECT LAST_INSERT_ID()")
        id_annonce = cursor.fetchone()

        photos_query = "INSERT INTO Photos_Annonces (url_photo, id_annonce) VALUES (%s, %s)"
        for photo in photos_annonce:
            cursor.execute(photos_query, (id_annonce, photo))

        cursor.execute("COMMIT;")

        return jsonify({'message': 'Vote annonce a été ajoutée avec succès!'})

    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout de l'annonce : {str(e)}"


# ROUTE
def supprimer_une_annonce():
    try:
        id_annonce = request.form.get('id_annonce')

        supp_annonce = "DELETE FROM Annonces WHERE id_annonce = %s"

        cursor.execute(supp_annonce, id_annonce)
        db_connection.commit()

        return jsonify({'message': 'Vote annonce a été supprimée.'})

    except Exception as e:
        return f"Une erreur s'est produite lors de la suppression de l'annonce : {str(e)}"


# ROUTE
def select_annonce(id_annonce):
    try:
        query = "SELECT * FROM Annonces WHERE id_annonce ={}".format(id_annonce)

        cursor.execute(query)
        annonce = cursor.fetchone()

        return annonce

    except Exception as e:
        return f"Une erreur s'est produite lors du chargement de la page : {str(e)}"


# ROUTE
def select_livre(id_livre):
    try:
        query = "SELECT * FROM Livres WHERE id_livre ={}".format(id_livre)

        cursor.execute(query)
        livre = cursor.fetchone()

        return livre

    except Exception as e:
        return f"Une erreur s'est produite lors du chargement de la page : {str(e)}"


# ROUTE
def ajouter_annonce_panier(id_panier, id_annonce):
    try:
        query = """INSERT INTO PanierAnnonce (id_panier, id_annonce) VALUES ("{}","{}")""".format(id_panier, id_annonce)

        cursor.execute(query)
        db_connection.commit()

    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout de l'annonce au panier : {str(e)}"


@app.route('/panier', methods=['GET'])
def select_panier_utilisateur(adresse_utilisateur):
    request = "SELECT * FROM Panier WHERE adresse_courriel ={}".format(adresse_utilisateur)
    cursor.execute(request)
    num_panier = cursor.fetchone()

    request2 = "SELECT EXISTS(SELECT * FROM PanierAnnonce WHERE id_panier = {}".format(num_panier[0])
    cursor.execute(request2)
    annonce_panier = cursor.fetchall()

    if annonce_panier[0][0] == 0:
        return ()
    else:
        return annonce_panier


@app.route('/panier', methods=['GET'])
def select_details_panier_utilisateur(adresse_utilisateur):
    try:
        # Sélectionner les détails des annonces dans le panier de l'utilisateur
        request = """
        SELECT Annonce.titre_annonce, Annonce.prix 
        FROM PanierAnnonce 
        JOIN Annonces ON PanierAnnonce.annonce = Annonces.id_annonce 
        WHERE id_panier = (
            SELECT id_panier 
            FROM Panier 
            WHERE adresse_courriel = '{}'
        )
        """.format(adresse_utilisateur)

        cursor.execute(request)
        details_panier = cursor.fetchall()

        return details_panier

    except Exception as e:
        return f"Une erreur s'est produite lors du chargement du panier : {str(e)}"


# ROUTE
def select_commentaire_annonce(id_annonce):
    try:
        query = "SELECT * FROM Commentaire WHERE annonce = {}".format(id_annonce)

        cursor.execute(query)
        commentaire = cursor.fetchall()
        return commentaire

    except Exception as e:
        return f"Une erreur s'est produite lors du chargement de la page : {str(e)}"


# ROUTE
def ajouter_commentaire(utilisateur, commentaire, id_annonce):
    try:
        query = """INSERT INTO Commentaire (auteur, commentaire, id_annonce, id_livre) 
        VALUES (CURRENT_DATE, "{}","{}","{}")""".format(utilisateur, commentaire, id_annonce)

        cursor.execute(query)
        db_connection.commit()

    except Exception as e:
        return f"Une erreur s'est produite lors de l'ajout du commentaire : {str(e)}"


# ROUTE
def passer_commande():
    try:
        adresse_utilisateur = session['adresse_utilisateur']
        adresse_vendeur = request.form.get('adresse_vendeur')
        montant = request.form.get('prix')

        cursor.execute("SELECT PA.annonce FROM Panier as P JOIN PanierAnnonce as PA on P.id_panier = PA.panier "
                       "WHERE P.adresse_utilisateur = %s",
                       (adresse_utilisateur,))
        annonce_panier = cursor.fetchall()

        cursor.execute("SELECT id_historique FROM Historiques_Transactions "
                       "WHERE adresse_utilisateur = %s", (adresse_utilisateur))
        id_historique = cursor.fetchall()

        cursor.execute("INSERT INTO Transactions (id_historique, id_annonce, "
                       "adresse_vendeur, adresse_acheteur, date, montant) "
                       "VALUES (%s, %s, %s, %s, current_date(), %s)",
                       (id_historique, annonce_panier, adresse_utilisateur, adresse_vendeur, montant,))

        cursor.execute("UPDATE Annonces SET statut = 'Vendu' WHERE id_annonce = %s", (annonce_panier,))

        cursor.execute("DELETE FROM PanierAnnonce WHERE panier = (SELECT id_panier FROM Panier "
                       "WHERE adresse_utilisateur = %s)", (adresse_utilisateur,))

        db_connection.commit()

    except Exception as e:
        return f"Une erreur s'est produite lors du passage de la commande : {str(e)}"


# Annonces avec leur derniere photo ajoutée
def select_all_annonce():
    # request = "SELECT * FROM Annonces;"
    request = ("SELECT A.*, MAX(P.url_photo) FROM Annonces A "
               "LEFT JOIN Galerie G ON A.id_annonce = G.id_annonce "
               "LEFT JOIN Photo P ON G.id_galerie = P.galerie GROUP BY A.id_annonce");
    cursor.execute(request)
    annonces = cursor.fetchall()
    return annonces


# Annonces par genre avec leur derniere photo ajoutée
def select_genre_annonce(genre):
    if isinstance(genre, list):
        genres_str = ', '.join([f"'{g.strip()}'" for g in genre])
    else:
        genres_str = genre
    request = ("SELECT A.*, MAX(P.url_photo) AS first_photo FROM Annonces A "
               "LEFT JOIN Galerie G ON A.id_annonce = G.id_annonce "
               "LEFT JOIN Photo P ON G.id_galerie = P.galerie "
               f"WHERE A.genre IN ({genres_str}) GROUP BY A.id_annonce")
    cursor.execute(request)
    annonces = cursor.fetchall()
    return annonces


# Annonces par mot clés avec leur derniere photo ajoutée
def recherche_annonce(terme_recherche):
    request = ("SELECT A.*, MAX(P.url_photo) AS first_photo FROM Annonces A "
               "LEFT JOIN Galerie G ON A.id_annonce = G.id_annonce "
               "LEFT JOIN Photo P ON G.id_galerie = P.galerie "
               "WHERE A.titre_annonce LIKE %s GROUP BY A.id_annonce")
    cursor.execute(request, ('%' + terme_recherche + '%',))
    annonces = cursor.fetchall()

    return annonces
