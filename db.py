import sqlite3
from db_requetes import *

bdd_name = "openeduc.db"


conn = sqlite3.connect(bdd_name)
cur = conn.cursor()

init_database()

# Ecole
cur.execute("""
INSERT INTO Ecole (nomEcole, Adresse, Ville, CodePostal, nbEleves, Telephone, Email, cycleScolaire)
VALUES ('ecole guynemer 2', '123 Rue de l Ecole', 'VilleABC', '12345', 300, '0123456789', 'ecoleabc@example.com', 'elementaire');
            """)
# Admin
cur.execute("""
INSERT INTO Utilisateur (identifiant, MotDePasse, isAdmin) 
VALUES ('administrateur', 'admin', true);
            """)
# User
cur.execute("""
INSERT INTO Utilisateur (identifiant, MotDePasse, isAdmin, idEcole) 
VALUES ('nidal', 'mdp', false, 1);
            """)

conn.commit()
conn.close()
