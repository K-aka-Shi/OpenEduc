import sqlite3, db_requetes

bdd_name = "openeduc.db"


conn = sqlite3.connect(bdd_name)
cur = conn.cursor()

db_requetes.creer_ecole()
db_requetes.creer_utilisateur()
db_requetes.creer_HistoriqueModification()
db_requetes.creer_personnel()
db_requetes.creer_classe()

#db_requetes.creer_triggers_utilisateur()
#db_requetes.creer_triggers_ecole()
#db_requetes.creer_triggers_personnel()
#db_requetes.creer_triggers_classe()


cur.execute("""
INSERT INTO Ecole (nomEcole, Adresse, Ville, CodePostal, nbEleves, Telephone, Email, cycleScolaire)
VALUES ('ecole guynemer 2', '123 Rue de l Ecole', 'VilleABC', '12345', 300, '0123456789', 'ecoleabc@example.com', 'elementaire');
            """)
conn.commit()            
    

conn.close()
