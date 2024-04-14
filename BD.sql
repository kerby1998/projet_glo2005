CREATE DATABASE if not exists LivreMarketBD;

USE LivreMarketBD;

#L'utilisateur qui s'inscrit sur le site doit fournir les 4 premiers attributs, s'il fait une commande, il devra aussi fournir
#les deux derniers qui pourront alors être enregistrés pour usage futur s'il le désire
CREATE TABLE if not exists Utilisateurs (adresse_courriel varchar(100) PRIMARY KEY ,
                                         prenom varchar(20) NOT NULL,
                                         nom varchar(20) NOT NULL,
                                         mot_de_passe varchar(100) NOT NULL,
                                         adresse_civique varchar(100) default NULL,
                                         num_tel varchar(12) default NULL);

#Les livres sont ajoutés à la BD par les adminsitrateurs lors de l'initialisation de la BD
CREATE TABLE if not exists Livres (id_livre int auto_increment PRIMARY KEY,
                                   titre_livre varchar(50) NOT NULL,
                                   auteur varchar(50) NOT NULL,
                                   description varchar(500) NOT NULL,
                                   annee year NOT NULL,
                                   genre enum('Fiction', 'Non-fiction', 'Romans','Thriller',
                                              'Science-fiction', 'Fantaisie', 'Mystère', 'Horreur',
                                              'Biographie', 'Autobiographie','Poésie', 'Drame',
                                              'Humour', 'Histoire', 'Science', 'Philosophie',
                                              'Art', 'Cuisine', 'Voyage','Religion', 'Spiritualité',
                                              'Éducation', 'Affaires', 'Finance', 'Santé', 'Mode de vie',
                                              'Sport', 'Technologie', 'Jeunesse', 'Aventure',
                                              'Classique', 'Théâtre', 'Fantastique') NOT NULL,
                                   isbn char(17) NOT NULL UNIQUE,
                                   url_photo varchar(500) NOT NULL);

#Les annonces sont ajoutées par les utilisateurs par l'entremise du site web
CREATE TABLE if not exists Annonces (id_annonce int auto_increment PRIMARY KEY,
                                     adresse_vendeur varchar(100),
                                     titre_annonce varchar(50) NOT NULL,
                                     description varchar(200),
                                     etat enum('Neuf', 'Usagé') NOT NULL,
                                     genre enum('Fiction', 'Non-fiction', 'Romans','Thriller',
                                                'Science-fiction', 'Fantaisie', 'Mystère', 'Horreur',
                                                'Biographie', 'Autobiographie','Poésie', 'Drame',
                                                'Humour', 'Histoire', 'Science', 'Philosophie',
                                                'Art', 'Cuisine', 'Voyage','Religion', 'Spiritualité',
                                                'Éducation', 'Affaires', 'Finance', 'Santé', 'Mode de vie',
                                                'Sport', 'Technologie', 'Jeunesse', 'Aventure',
                                                'Classique', 'Théâtre', 'Fantastique') NOT NULL,
                                     prix decimal(10,2) NOT NULL CHECK  (prix >= 0),
                                     statut enum('Disponible', 'Vendu') DEFAULT 'Disponible',
                                     date_affichage timestamp DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (adresse_vendeur) REFERENCES Utilisateurs(adresse_courriel) ON DELETE CASCADE ON UPDATE CASCADE);

#Au moins une photo doit être ajoutée avec chaque annonce
CREATE TABLE if not exists Photos_Annonces (id_photo int auto_increment PRIMARY KEY ,
                                             url_photo varchar(500) NOT NULL,
                                             id_annonce int NOT NULL,
                           FOREIGN KEY (id_annonce) REFERENCES Annonces(id_annonce) ON DELETE CASCADE ON UPDATE CASCADE);

#Chaque client possède une liste de souhaits
CREATE TABLE if not exists Listes_Souhaits (id_souhaits int auto_increment PRIMARY KEY,
                                            adresse_utilisateur varchar(100) UNIQUE,
                           FOREIGN KEY (adresse_utilisateur) REFERENCES Utilisateurs(adresse_courriel) ON DELETE CASCADE ON UPDATE CASCADE);

#Cette liste de souhait contient des annonces ou des livres auquels le client est intéressé
CREATE TABLE if not exists Contenu_Liste_Souhaits (id_contenu int auto_increment PRIMARY KEY, #à enlever
                                                   id_liste int NOT NULL,
                                                   id_livre int DEFAULT NULL,
                                                   id_annonce int,
                           FOREIGN KEY (id_liste) REFERENCES Listes_Souhaits(id_souhaits) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (id_livre) REFERENCES Livres(id_livre) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (id_annonce) REFERENCES Annonces(id_annonce) ON DELETE CASCADE ON UPDATE CASCADE);

#Chaque client possède un historique de transactions
CREATE TABLE if not exists Historiques_Transactions (id_historique int auto_increment PRIMARY KEY,
                                                     adresse_utilisateur varchar(100) UNIQUE,
                           FOREIGN KEY (adresse_utilisateur) REFERENCES Utilisateurs(adresse_courriel) ON UPDATE CASCADE ON DELETE CASCADE);

#Chaque transaction est ajoutée à l'historique de l'acheteur lors d'une vente (voir requêtes)
CREATE TABLE if not exists Transactions (id_transaction int auto_increment PRIMARY KEY,
                                         id_historique int,
                                         id_annonce int,
                                         adresse_vendeur varchar(100),
                                         adresse_acheteur varchar(100),
                                         date date,
                                         montant decimal(10,2) NOT NULL,
                           FOREIGN KEY (id_historique) REFERENCES Historiques_Transactions(id_historique) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (id_annonce) REFERENCES Annonces(id_annonce) ON DELETE CASCADE ON UPDATE CASCADE,
                           FOREIGN KEY (adresse_vendeur) REFERENCES Utilisateurs(adresse_courriel) ON UPDATE CASCADE ON DELETE CASCADE,
                           FOREIGN KEY (adresse_acheteur) REFERENCES Utilisateurs(adresse_courriel) ON UPDATE CASCADE ON DELETE CASCADE);
                           /*FOREIGN KEY (montant) REFERENCES Annonces(prix) ON DELETE CASCADE ON UPDATE CASCADE)*/

#Les commentaires postés par les utilisateurs sur les annonces ou les pages de livre
CREATE TABLE if not exists Commentaires (id_commentaire int auto_increment PRIMARY KEY,
                                         date timestamp DEFAULT CURRENT_TIMESTAMP,
                                         auteur varchar(50),
                                         commentaire text,
                                         id_annonce int DEFAULT NULL,
                                         id_livre int DEFAULT NULL,
                            FOREIGN KEY (auteur) REFERENCES Utilisateurs(adresse_courriel) ON UPDATE CASCADE ON DELETE CASCADE,
                            FOREIGN KEY (id_annonce) REFERENCES Annonces(id_annonce) ON DELETE CASCADE ON UPDATE CASCADE,
                            FOREIGN KEY (id_livre) REFERENCES Livres(id_livre) ON DELETE CASCADE ON UPDATE CASCADE);

#Chaque utilisateur à un panier
CREATE TABLE if not exists  Panier (id_panier int auto_increment PRIMARY KEY,
                                    adresse_utilisateur varchar(50),
                            FOREIGN KEY (adresse_utilisateur) REFERENCES Utilisateurs(adresse_courriel) ON UPDATE CASCADE ON DELETE CASCADE);

#Chaque panier d'utilisateur contient les annonces que celui-ci veut acheter
CREATE TABLE IF NOT EXISTS PanierAnnonce(panier integer,
                                         annonce integer PRIMARY KEY,
                            FOREIGN KEY (panier) REFERENCES Panier(id_panier) ON DELETE CASCADE ON UPDATE CASCADE,
                            FOREIGN KEY (annonce) REFERENCES Annonces(id_annonce) ON DELETE CASCADE ON UPDATE CASCADE);


DELIMITER //

#Gâchette permettant de valider le format du numéro de téléphone de l'utilisateur
    CREATE TRIGGER NumeroTelValide
         BEFORE INSERT ON Utilisateurs
         FOR EACH ROW
         BEGIN
             IF NOT(NEW.num_tel COLLATE utf8mb4_bin REGEXP '^^[0-9]{3}-[0-9]{3}-[0-9]{4}$')
                 THEN
                 SIGNAL SQLSTATE '45000'
                 SET MESSAGE_TEXT = 'Le numéro de téléphone est invalide, il doit être de format ###-###-####';
             end if;
     END//

#Gâchette permettant de valider le format de l'adresse courriel de l'utilisateur
    CREATE TRIGGER AdresseCourrielValide
        BEFORE INSERT ON Utilisateurs
        FOR EACH ROW
        BEGIN
            IF NOT(NEW.adresse_courriel COLLATE utf8mb4_bin REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z]+\.+[a-zA-Z]{2,}$')
                THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Adresse courriel est invalide !';
            end if;
        END //

#Un panier, une liste de souhait et un historique sont automatiquement crées pour chaque nouvel utilisateur
    CREATE TRIGGER AssignerPanier
        AFTER INSERT ON Utilisateurs
        FOR EACH ROW
        BEGIN
        INSERT INTO Panier (adresse_utilisateur) VALUE (NEW.adresse_courriel);
        END //

    CREATE TRIGGER AssignerListeSouhaits
        AFTER INSERT ON Utilisateurs
        FOR EACH ROW
        BEGIN
            INSERT INTO Listes_Souhaits(adresse_utilisateur) VALUE (NEW.adresse_courriel);
        END //

    CREATE TRIGGER AssignerHistorique
        AFTER INSERT ON Utilisateurs
        FOR EACH ROW
        BEGIN
            INSERT INTO Historiques_Transactions(adresse_utilisateur) VALUE (NEW.adresse_courriel);
        end //

#Chaque annonce doit obligatoirement avoir au moins une photo l'accompagnant
    CREATE TRIGGER AjoutPhotoAnnonce
        BEFORE INSERT ON Annonces
        FOR EACH ROW
        BEGIN
            DECLARE compteur int;
            SELECT COUNT(*) INTO compteur FROM Photos_Annonces WHERE id_annonce = NEW.id_annonce;
            IF compteur = 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Vous devez ajouter au moins une image avec votre annonce.';
            END IF;
        END //

    #CREATE TRIGGER MotDePasseValide
        #BEFORE INSERT ON Utilisateurs
        #FOR EACH ROW
        #BEGIN
            #IF NOT( CHAR_LENGTH(NEW.mot_de_passe) >= 8)
                #THEN
                #SIGNAL SQLSTATE '45000'
                #SET MESSAGE_TEXT = 'Le mot de passe doit avoir au moins 8 charactere !';
            #end if;
            #IF NOT(NEW.mot_de_passe COLLATE utf8mb4_bin REGEXP '[A-Z]')
                #THEN
                #SIGNAL SQLSTATE '45000'
                #SET MESSAGE_TEXT = 'Le mot de passe doit avoir au moins 1 majuscule !';
            #end if;
            #IF NOT(NEW.mot_de_passe COLLATE utf8mb4_bin REGEXP '[a-z]')
                #THEN
                #SIGNAL SQLSTATE '45000'
                #SET MESSAGE_TEXT = 'Le mot de passe doit avoir au moins 1 minuscule !';
            #end if;
            #IF NOT(NEW.mot_de_passe REGEXP '[0-9]')
                #THEN
                #SIGNAL SQLSTATE '45000'
                #SET MESSAGE_TEXT = 'Le mot de passe doit avoir au moins 1 chiffre !';
            #end if;
        #END//

DELIMITER ;


CREATE INDEX idx_adresse_courriel ON Utilisateurs(adresse_courriel);
CREATE INDEX idx_id_annonce ON Annonces(id_annonce);
CREATE INDEX idx_nom_annonce ON Annonces(titre_annonce);
CREATE INDEX idx_nom_categorie_annonce ON Annonces(titre_annonce, genre);
CREATE INDEX idx_titre_etat_annonce ON Annonces(titre_annonce, etat);
CREATE INDEX idx_categorie_livre ON Livres (titre_livre, genre);
CREATE INDEX idx_nom_livre ON Livres(titre_livre);