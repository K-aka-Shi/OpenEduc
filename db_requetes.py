import sqlite3

bdd_name = "openeduc.db"


def init_database() :
    # Tables
    creer_ecole()
    creer_utilisateur()
    creer_HistoriqueModification()
    creer_personnel()
    creer_classe()
    # Triggers
    creer_triggers_utilisateur()
    creer_triggers_personnel()
    creer_triggers_classe()
    creer_triggers_ecole()


# ____________________________________________________________________________________________________
#                                       CREATE TABLE
# ____________________________________________________________________________________________________

# ECOLE
# TODO: école publique/privé ?
def creer_ecole():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Ecole")
    cur.execute("""
CREATE TABLE IF NOT EXISTS Ecole (
idEcole INTEGER PRIMARY KEY,
nomEcole VARCHAR(255),
Adresse VARCHAR(255),
Ville VARCHAR(288),
CodePostal VARCHAR(10),
nbEleves INT,
Telephone VARCHAR(15),
Email VARCHAR(255),
cycleScolaire TEXT CHECK( cycleScolaire IN ('maternelle','elementaire','college','lycee') )
);
                """)
    conn.close()


# Utilisateur

def creer_utilisateur():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Utilisateur")
    cur.execute("""
CREATE TABLE IF NOT EXISTS Utilisateur (
idUtilisateur INTEGER PRIMARY KEY ,
Identifiant VARCHAR(255),
MotDePasse VARCHAR(255),
isAdmin BOOLEAN,
idEcole INT,
FOREIGN KEY (idEcole) REFERENCES Ecole(idEcole)
);
                """)
    conn.close()




# HistoriqueModification

def creer_HistoriqueModification():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS HistoriqueModification")
    cur.execute("""
CREATE TABLE IF NOT EXISTS HistoriqueModification (
idHistorique INTEGER PRIMARY KEY,
idUtilisateur INT,
idEcole INT,
dateModification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
champsModifies VARCHAR(255),
ancienneValeur VARCHAR(255),
nouvelleValeur VARCHAR(255),
FOREIGN KEY (idUtilisateur) REFERENCES Utilisateur(idUtilisateur),
FOREIGN KEY (idEcole) REFERENCES Ecole(idEcole) ON DELETE CASCADE
);
                """)
    conn.close()


# Personnel

def creer_personnel():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Personnel")
    cur.execute("""
CREATE TABLE Personnel (
idPersonnel INTEGER PRIMARY KEY ,
Nom VARCHAR(50),
Prenom VARCHAR(50),
Sexe TEXT CHECK( Sexe IN ('H','F') ),
Telephone VARCHAR(15),
Email VARCHAR(255),
Fonction VARCHAR(100),
idEcole INT, -- Clé étrangère faisant référence à l'école à laquelle le personnel est rattaché
idClasse INT,
FOREIGN KEY (idEcole) REFERENCES Ecole(idEcole),
FOREIGN KEY (idClasse) REFERENCES Classe(idClasse)
);
                """)
    conn.close()



# Classe

def creer_classe():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Classe")
    cur.execute("""
CREATE TABLE Classe (
idClasse INTEGER PRIMARY KEY,
Effectif INT,
Moyenne FLOAT,
cycleScolaire TEXT CHECK( cycleScolaire IN ('CP','CE1','CE2','CM1','CM2','6E','5E','4E','3E','1RE','2NDE','TALE') ),
idPersonnel INT,
idEcole INT, -- Clé étrangère faisant référence à l'école à laquelle la classe est rattachée
FOREIGN KEY (idEcole) REFERENCES Ecole(idEcole),
FOREIGN KEY (idPersonnel) REFERENCES Personnel(idPersonnel),
FOREIGN KEY (cycleScolaire) REFERENCES Ecole(cycleScolaire)
);
                """)
    conn.close()

# ____________________________________________________________________________________________________
#                                       SELECT                                                       |
# ___________________________________________________________________________________________________|

# Utilisateur
def chercher_utilisateurAll() :
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM Utilisateur")
    utilisateur = res.fetchall()
    print("Resultat requete :",utilisateur)
    conn.close()
    return utilisateur

def chercher_utilisateur(username,password) :
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    res = cur.execute("""
                      SELECT * FROM Utilisateur
                      WHERE Identifiant = :identifiant AND MotDePasse = :mdp
                      """, {'identifiant':username, 'mdp':password}
                      )
    utilisateur = res.fetchall()
    print("chercher_utilisateur :",utilisateur)
    conn.close()
    return utilisateur

def chercher_utilisateurLike(username) :
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    res = cur.execute("""SELECT * FROM Utilisateur
                      WHERE Identifiant LIKE ?""", ('%' + username + '%',)
    )
    utilisateur = res.fetchall()
    print("Resultat requete :",utilisateur)
    conn.close()
    return utilisateur

def supprimer_utilisateurByID(ids) :
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    print("\n\n\n")
    for id in ids :
        print("liste des trucs qui seront effacés :",ids)
        cur.execute("""
                    DELETE FROM Utilisateur WHERE idUtilisateur = ?
                    """, (id,)
        )
    conn.commit()
    conn.close()

# Ecole
def chercher_ecole(saisie) :
    """
    ## Fonction
    Retourne les informations d'une école.

    ## Parameters:
    saisie (str) : le nom d'une école.

    ## Returns:
    ecole (liste) : La liste d'information.
    """
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    res = cur.execute("""
        SELECT nomEcole,Adresse,Ville,CodePostal,nbEleves,Telephone,Email,cycleScolaire
        FROM Ecole WHERE nomEcole LIKE ?""", ('%' + saisie + '%',)
    )
    ecole = res.fetchall()
    print("Resultat requete :",ecole)
    conn.close()
    return ecole

def chercher_ecoleAll() :
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    res = cur.execute("""
                      SELECT idEcole,nomEcole,Adresse,Ville,CodePostal,nbEleves,Telephone,Email,cycleScolaire
                      FROM Ecole
                      """)
    ecoles = res.fetchall()
    conn.close()
    return ecoles

def chercher_ecole_formCreerReferent():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    res = cur.execute("""
                      SELECT idEcole,nomEcole,cycleScolaire,Ville,CodePostal
                      FROM Ecole
                      """)
    ecole = res.fetchall()
    print("Resultat requete :",ecole)
    conn.close()
    return ecole


# ____________________________________________________________________________________________________
#                                       INSERT                                                       |
# ___________________________________________________________________________________________________|
def generer_mdp() :
    import secrets, string, random

    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation
    selection_list = letters + digits + special_chars
    password_len = 10

    while True:
        password = ''
        for i in range(password_len):
            password += ''.join(secrets.choice(selection_list))
        if (any(char in special_chars for char in password) and 
        sum(char in digits for char in password)>=2):
            break
    print(password)
    return(password)


def inserer_referent(identifiant, idEcole):
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    password = generer_mdp()
    cur.execute("""
        INSERT INTO Utilisateur (identifiant, MotDePasse, isAdmin, idEcole) 
        VALUES (:identifiant, :mdp, false, :idEcole);
            """, {'identifiant':identifiant,'mdp':password,'idEcole':idEcole})
    conn.commit()
    conn.close()
    return password

# ____________________________________________________________________________________________________
#                                         TRIGGERS
# ____________________________________________________________________________________________________
    

# Utilisateur
def creer_triggers_utilisateur():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    # Trigger pour l'insertion
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS utilisateur_insert_trigger
    AFTER INSERT ON Utilisateur
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NEW.idUtilisateur, NEW.idEcole, 'Insertion Utilisateur', NULL, NEW.identifiant || ' ' || NEW.MotDePasse);
    END;
    """)
    # Trigger pour la mise à jour
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS utilisateur_update_trigger
    AFTER UPDATE ON Utilisateur
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NEW.idUtilisateur, NEW.idEcole, 'Mise à jour Utilisateur', NULL, NULL);
    END;
    """)
    # Trigger pour la suppression
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS utilisateur_delete_trigger
    AFTER DELETE ON Utilisateur
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (OLD.idUtilisateur, OLD.idEcole, 'Suppression Utilisateur', NULL, NULL);
    END;
    """)
    conn.commit()
    conn.close()



# Ecole
def creer_triggers_ecole():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    # Trigger pour l'insertion
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS ecole_insert_trigger
    AFTER INSERT ON Ecole
    BEGIN
        INSERT INTO HistoriqueModification (idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NEW.idEcole, 'Insertion Ecole', NULL, NULL);
    END;
    """)
    # Trigger pour la mise à jour
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS ecole_update_trigger
    AFTER UPDATE ON Ecole
    BEGIN
        INSERT INTO HistoriqueModification (idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NEW.idEcole, 'Mise à jour Ecole', NULL, NULL);
    END;
    """)
    # Trigger pour la suppression
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS ecole_delete_trigger
    AFTER DELETE ON Ecole
    BEGIN
        INSERT INTO HistoriqueModification (idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (OLD.idEcole, 'Suppression Ecole', NULL, NULL);
    END;
    """)
    conn.commit()
    conn.close()



# Personnel
def creer_triggers_personnel():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    # Trigger pour l'insertion
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS personnel_insert_trigger
    AFTER INSERT ON Personnel
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NULL, NEW.idEcole, 'Insertion Personnel', NULL, NULL);
    END;
    """)
    # Trigger pour la mise à jour
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS personnel_update_trigger
    AFTER UPDATE ON Personnel
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NULL, NEW.idEcole, 'Mise à jour Personnel', NULL, NULL);
    END;
    """)
    # Trigger pour la suppression
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS personnel_delete_trigger
    AFTER DELETE ON Personnel
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NULL, OLD.idEcole, 'Suppression Personnel', NULL, NULL);
    END;
    """)
    conn.commit()
    conn.close()


# Classe
def creer_triggers_classe():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    # Trigger pour l'insertion
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS classe_insert_trigger
    AFTER INSERT ON Classe
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NULL, NEW.idEcole, 'Insertion Classe', NULL, NULL);
    END;
    """)
    # Trigger pour la mise à jour
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS classe_update_trigger
    AFTER UPDATE ON Classe
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NULL, NEW.idEcole, 'Mise à jour Classe', NULL, NULL);
    END;
    """)
    # Trigger pour la suppression
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS classe_delete_trigger
    AFTER DELETE ON Classe
    BEGIN
        INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur)
        VALUES (NULL, OLD.idEcole, 'Suppression Classe', NULL, NULL);
    END;
    """)
    conn.commit()
    conn.close()






# ____________________________________________________________________________________________________
#                                         INSERT
# ____________________________________________________________________________________________________
    



def inserer_donnees():
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()

    # Données pour la table Ecole
    ecoles = [
        ("École des Lilas", "10 Rue des Lilas", "Paris", "75020", 300, "01 23 45 67 89", "ecole.lilas@example.com", "elementaire"),
        ("Collège Marcel Pagnol", "22 Avenue de la République", "Marseille", "13001", 500, "04 56 78 90 12", "college.pagnol@example.com", "college"),
        ("Lycée Victor Hugo", "15 Rue Victor Hugo", "Lyon", "69001", 800, "06 78 90 12 34", "lycee.hugo@example.com", "lycee"),
        ('École Guynemer II', '16 Rue de Châteauroux', 'Strasbourg', '67000', 1000, '0388344130', 'ce.0670384D@ac-strasbourg.fr', 'elementaire'),
        ('Ecole du Centre', "4 rue de l'Ecole", 'Lingolsheim', '67380', 200, '0388780432', 'ce.0671418C@ac-strasbourg.fr', 'elementaire')
    ]

    # Données pour la table Utilisateur
    utilisateurs = [
        ("administrateur", "admin", True, None),
        ("nidal", "mdp", False, 1),
        ("leandre", "mdp", False, 2)
    ]

    # Données pour la table Personnel
    personnel = [
        ("Dupont", "Jean", "H", "01 23 45 67 89", "jean.dupont@example.com", "Enseignant", 1, None),
        ("Durand", "Marie", "F", "04 56 78 90 12", "marie.durand@example.com", "Directrice", 2, None)
    ]

    # Données pour la table Classe
    classes = [
        (25, 12.5, "CP", 1, 1),
        (30, 14.2, "CE1", 2, 1),
        (28, 13.8, "6E", 3, 2)
    ]

    # Insertion des données dans chaque table
    cur.executemany("INSERT INTO Ecole (nomEcole, Adresse, Ville, CodePostal, nbEleves, Telephone, Email, cycleScolaire) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ecoles)
    cur.executemany("INSERT INTO Utilisateur (Identifiant, MotDePasse, isAdmin, idEcole) VALUES (?, ?, ?, ?)", utilisateurs)
    cur.executemany("INSERT INTO Personnel (Nom, Prenom, Sexe, Telephone, Email, Fonction, idEcole, idClasse) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", personnel)
    cur.executemany("INSERT INTO Classe (Effectif, Moyenne, cycleScolaire, idPersonnel, idEcole) VALUES (?, ?, ?, ?, ?)", classes)

    conn.commit()
    conn.close()







# ____________________________________________________________________________________________________
#                                         UPDATE
# ____________________________________________________________________________________________________
    
def update_referent(id_utilisateur, identifiant, password, idEcole):
    conn = sqlite3.connect(bdd_name)
    cur = conn.cursor()
    if identifiant :
        print("requete identifiant")
        cur.execute("""
                    UPDATE Utilisateur
                    SET Identifiant = :nouvel_identifiant
                    WHERE idUtilisateur = :id_utilisateur;
                    """, {'nouvel_identifiant':identifiant, 'id_utilisateur':id_utilisateur}
                    )
    if password :
        print("requete mdp")
        cur.execute("""
                    UPDATE Utilisateur
                    SET MotDePasse = :nouveau_mdp
                    WHERE idUtilisateur = :id_utilisateur;
                    """, {'nouveau_mdp':password, 'id_utilisateur':id_utilisateur}
                    )
    if idEcole:
        print("requete l'idEcole")
        cur.execute("""
                    UPDATE Utilisateur
                    SET idEcole = :nouvelle_ecole
                    WHERE idUtilisateur = :id_utilisateur;
                    """, {'nouvelle_ecole':idEcole, 'id_utilisateur':id_utilisateur}
                    )
    conn.commit()
    conn.close()