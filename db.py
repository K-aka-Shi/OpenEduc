from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Ecole, Utilisateur, Personnel, Classe, HistoriqueModification

db_path = 'sqlite:///test_openeduc.db'

engine = create_engine(db_path)

try :
    conn = engine.connect()
    print("success")
 
    Base.metadata.drop_all(bind=conn)
    Base.metadata.create_all(bind=conn)

    Session = sessionmaker(bind=conn)
    session = Session()

    centreLingo = Ecole(idEcole=1,
                        nomEcole = "Ecole du centre",
                        Adresse = "4 rue de l'école",
                        Ville = "Lingomsheim",
                        CodePostal = "67380",
                        nbEleves = 300,
                        Telephone="03030303",
                        Email="mail@gmail.com",
                        cycleScolaire="elementaire")
    session.add(centreLingo)
    session.commit()

    conn.commit()
except Exception as ex :
    print(ex)





















# import sqlite3
# from db_requetes import *

# bdd_name = "openeduc.db"


# conn = sqlite3.connect(bdd_name)
# cur = conn.cursor()

# init_database()

# # Ecole
# cur.execute("""
# INSERT INTO Ecole (nomEcole, Adresse, Ville, CodePostal, nbEleves, Telephone, Email, cycleScolaire)
# VALUES ('École Guynemer II', '16 Rue de Châteauroux', 'Strasbourg', '67000', 1000, '0388344130', 'ce.0670384D@ac-strasbourg.fr', 'elementaire'),
#         ('Ecole du Centre', "4 rue de l'Ecole", 'Lingolsheim', '67380', 200, '0388780432', 'ce.0671418C@ac-strasbourg.fr', 'elementaire');
#             """)


# # Admin
# cur.execute("""
# INSERT INTO Utilisateur (identifiant, MotDePasse, isAdmin) 
# VALUES ('administrateur', 'admin', true);
#             """)
# # User
# cur.execute("""
# INSERT INTO Utilisateur (identifiant, MotDePasse, isAdmin, idEcole) 
# VALUES ('nidal', 'mdp', false, 1);
#             """)

# conn.commit()
# conn.close()
