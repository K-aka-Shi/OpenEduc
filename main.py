from flask import Flask, render_template, url_for, redirect, request, session, flash
from dotenv import load_dotenv
import os
from db_requetes import *


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("APP_SECRET_KEY")

@app.route("/")
def index():
    return render_template("views/index.html")

# _________________________________________________
#                   NAVIGATION                    
# _________________________________________________

###################
#    CONNEXION    #
###################

@app.route("/login", methods=["POST", "GET"])
def login() :
    if request.method == "POST" :
        data = request.form
        username = data.get("username")
        password = data.get("password")
        utilisateur = chercher_utilisateur(username,password)
        if utilisateur != [] :
            utilisateur = utilisateur[0]
            session["username"] = utilisateur[1]
            session["statut"] = utilisateur[3]
            print(session.get("username"), session.get("statut"))
            return redirect(url_for('dashboard'))
        else :
            print("utilisateur inconnu")
            return redirect(request.url)
    else :
        return render_template("views/login.html")

@app.route("/logout")
def logout() :
    session.pop('username', None)
    return redirect(url_for('index'))


###################
#    DASHBOARD    #
###################

@app.route("/dashboard")
def dashboard() :
    username = session.get("username")
    statut = session.get("statut")
    if username is not None :
        if statut == 1 :
            ecoles = chercher_ecole_formCreerReferent()
            print(ecoles)
        return render_template("views/dashboard.html",
                               isAdmin=statut,
                               ecoles = ecoles)
    return redirect(url_for('login'))

@app.route("/ajouter_referent", methods=["POST"])
def addReferent() :
    return redirect(url_for('dashboard'))

###################
#    RECHERCHE    #
###################

@app.route("/recherche", methods=["POST", "GET"])
def recherche() :
    if request.method == "POST":
        # si le formulaire est envoyé
        data = request.form
        saisie = data.get('nom')
        print("Saisie :",saisie)
        resultats = chercher_ecole(saisie)
        tab = [res for res in resultats]
        print(tab)
        # resultats = [1:]
        print(resultats)
    else:
        # méthode GET
        resultats = None
    return render_template("views/recherche.html", resultats=resultats)


@app.route("/partenaires")
def partenaires() :
    return render_template("views/partenaires.html")



# _________________________________________________
#                   LEGAL                    
# _________________________________________________


@app.route("/protection-des-donnees")
def protectionDesDonnees() :
    return render_template("views/legal/protection-des-donnees.html")


@app.route("/mentions-legales")
def mentionsLegales() :
    return render_template("views/legal/mentions-legales.html")


@app.route("/cgu")
def cgu() :
    return render_template("views/legal/cgu.html")





@app.errorhandler(404)
def not_found(e):
  return render_template('error404.html'), 404