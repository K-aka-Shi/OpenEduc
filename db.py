import sqlite3
from db_requetes import *

bdd_name = "openeduc.db"


conn = sqlite3.connect(bdd_name)
cur = conn.cursor()

init_database()

# Ecole
cur.execute("""
INSERT INTO Ecole (nomEcole, Adresse, Ville, CodePostal, nbEleves, Telephone, Email, cycleScolaire)
VALUES ('École Guynemer II', '16 Rue de Châteauroux', 'Strasbourg', '67000', 1000, '0388344130', 'ce.0670384D@ac-strasbourg.fr', 'elementaire'),
        ('Ecole du Centre', "4 rue de l'Ecole", 'Lingolsheim', '67380', 200, '0388780432', 'ce.0671418C@ac-strasbourg.fr', 'elementaire');
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
