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

def chercher_ecole(saisie) :
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
