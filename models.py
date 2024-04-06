
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()

# Defining the Ecole table
class Ecole(Base):
    __tablename__ = 'Ecole'
    idEcole = Column(Integer, primary_key=True)
    nomEcole = Column(String(255))
    Adresse = Column(String(255))
    Ville = Column(String(288))
    CodePostal = Column(String(10))
    nbEleves = Column(Integer)
    Telephone = Column(String(15))
    Email = Column(String(255))
    cycleScolaire = Column(String, CheckConstraint('cycleScolaire IN ("maternelle", "elementaire", "college", "lycee")'))

# Defining the Utilisateur table
class Utilisateur(Base):
    __tablename__ = 'Utilisateur'
    idUtilisateur = Column(Integer, primary_key=True)
    Identifiant = Column(String(255))
    MotDePasse = Column(String(255))
    isAdmin = Column(Boolean)
    idEcole = Column(Integer, ForeignKey('Ecole.idEcole'))
    ecole = relationship("Ecole")

# Defining the HistoriqueModification table
class HistoriqueModification(Base):
    __tablename__ = 'HistoriqueModification'
    idHistorique = Column(Integer, primary_key=True)
    idUtilisateur = Column(Integer, ForeignKey('Utilisateur.idUtilisateur'))
    idEcole = Column(Integer, ForeignKey('Ecole.idEcole', ondelete='CASCADE'))
    dateModification = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    champsModifies = Column(String(255))
    ancienneValeur = Column(String(255))
    nouvelleValeur = Column(String(255))

# Defining the Personnel table
class Personnel(Base):
    __tablename__ = 'Personnel'
    idPersonnel = Column(Integer, primary_key=True)
    Nom = Column(String(50))
    Prenom = Column(String(50))
    Sexe = Column(String, CheckConstraint('Sexe IN ("H", "F")'))
    Telephone = Column(String(15))
    Email = Column(String(255))
    Fonction = Column(String(100))
    idEcole = Column(Integer, ForeignKey('Ecole.idEcole'))
    idClasse = Column(Integer, ForeignKey('Classe.idClasse'), use_alter=True)
    ecole = relationship("Ecole")
    classe = relationship("Classe", foreign_keys=[idClasse])  # Spécifier la clé étrangère

# Defining the Classe table
class Classe(Base):
    __tablename__ = 'Classe'
    idClasse = Column(Integer, primary_key=True)
    Effectif = Column(Integer)
    Moyenne = Column(Float)
    cycleScolaire = Column(String, CheckConstraint('cycleScolaire IN ("CP", "CE1", "CE2", "CM1", "CM2", "6E", "5E", "4E", "3E", "1RE", "2NDE", "TALE")'))
    idPersonnel = Column(Integer, ForeignKey('Personnel.idPersonnel'), use_alter=True)
    idEcole = Column(Integer, ForeignKey('Ecole.idEcole'))
    ecole = relationship("Ecole")
    personnel = relationship("Personnel", foreign_keys=[idPersonnel])  # Spécifier la clé étrangère


from sqlalchemy import event
from sqlalchemy import text
from models import  Base, Ecole, Classe, Utilisateur, Personnel, HistoriqueModification

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
