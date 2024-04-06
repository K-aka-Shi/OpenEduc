from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from models import Base, Ecole, Utilisateur, Personnel, Classe, HistoriqueModification

db_path = 'sqlite:///test_openeduc.db'

engine = create_engine(db_path)

# Définition des déclencheurs

# Définition des déclencheurs pour la table Utilisateur
@event.listens_for(Utilisateur, 'after_insert')
def after_insert_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (:idUtilisateur, :idEcole, 'Insertion Utilisateur', NULL, :nouvelleValeur)"),
        idUtilisateur=target.idUtilisateur,
        idEcole=target.idEcole,
        nouvelleValeur=target.Identifiant + ' ' + target.MotDePasse
    )

@event.listens_for(Utilisateur, 'after_update')
def after_update_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (:idUtilisateur, :idEcole, 'Mise à jour Utilisateur', NULL, NULL)"),
        idUtilisateur=target.idUtilisateur,
        idEcole=target.idEcole
    )

@event.listens_for(Utilisateur, 'after_delete')
def after_delete_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (:idUtilisateur, :idEcole, 'Suppression Utilisateur', NULL, NULL)"),
        idUtilisateur=target.idUtilisateur,
        idEcole=target.idEcole
    )


# Définition des déclencheurs pour la table Ecole
@event.listens_for(Ecole, 'after_insert')
def after_insert_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (:idEcole, 'Insertion Ecole', NULL, NULL)"),
        idEcole=target.idEcole
    )

@event.listens_for(Ecole, 'after_update')
def after_update_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (:idEcole, 'Mise à jour Ecole', NULL, NULL)"),
        idEcole=target.idEcole
    )

@event.listens_for(Ecole, 'after_delete')
def after_delete_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (:idEcole, 'Suppression Ecole', NULL, NULL)"),
        idEcole=target.idEcole
    )


# Définition des déclencheurs pour la table Personnel
@event.listens_for(Personnel, 'after_insert')
def after_insert_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (NULL, :idEcole, 'Insertion Personnel', NULL, NULL)"),
        idEcole=target.idEcole
    )

@event.listens_for(Personnel, 'after_update')
def after_update_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (NULL, :idEcole, 'Mise à jour Personnel', NULL, NULL)"),
        idEcole=target.idEcole
    )

@event.listens_for(Personnel, 'after_delete')
def after_delete_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (NULL, :idEcole, 'Suppression Personnel', NULL, NULL)"),
        idEcole=target.idEcole
    )


# Définition des déclencheurs pour la table Classe
@event.listens_for(Classe, 'after_insert')
def after_insert_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (NULL, :idEcole, 'Insertion Classe', NULL, NULL)"),
        idEcole=target.idEcole
    )

@event.listens_for(Classe, 'after_update')
def after_update_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (NULL, :idEcole, 'Mise à jour Classe', NULL, NULL)"),
        idEcole=target.idEcole
    )

@event.listens_for(Classe, 'after_delete')
def after_delete_listener(mapper, connection, target):
    connection.execute(
        text("INSERT INTO HistoriqueModification (idUtilisateur, idEcole, champsModifies, ancienneValeur, nouvelleValeur) VALUES (NULL, :idEcole, 'Suppression Classe', NULL, NULL)"),
        idEcole=target.idEcole
    )

# Fonction pour créer la session SQLAlchemy
def create_session():
    Session = sessionmaker(bind=engine)
    return Session()

try:
    conn = engine.connect()
    print("Success")
 
    Base.metadata.drop_all(bind=conn)
    Base.metadata.create_all(bind=conn)

    # Créer une session SQLAlchemy
    session = create_session()

    # Ajoutez vos données ici
    centreLingo = Ecole(idEcole=1,
                        nomEcole="Ecole du centre",
                        Adresse="4 rue de l'école",
                        Ville="Lingomsheim",
                        CodePostal="67380",
                        nbEleves=300,
                        Telephone="03030303",
                        Email="mail@gmail.com",
                        cycleScolaire="elementaire")
    session.add(centreLingo)
    session.commit()

    # Fermez la session après utilisation
    session.close()

    conn.commit()
except Exception as ex:
    print(ex)
