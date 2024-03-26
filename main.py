from flask import Flask, render_template, url_for, redirect, request, session, flash
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("APP_SECRET_KEY")

@app.route("/")
def index():
    return render_template("views/index.html")

# _________________________________________________
#                   NAVIGATION                    
# _________________________________________________


utilisateurs = [
    {"nom" : "admin", "password" : "admin"},
    {"nom" : "nidal", "password" : "azerty"}
    ]

@app.route("/login", methods=["POST", "GET"])
def login() :
    if request.method == "POST" :
        data = request.form
        username = data.get("username")
        password = data.get("password")
        utilisateur = search_user(username, password)
        if utilisateur is not None :
            session["username"] = utilisateur["nom"]
            print(session["username"])
            return redirect(url_for('dashboard'))
        else :
            print("utilisateur inconnu")
            return redirect(request.url)
    else :
        return render_template("views/login.html")

# --------- #
# Fonctions #
# --------- #


def search_user(nom, mdp) :
    for user in utilisateurs :
        if user["nom"] == nom and user["password"] == mdp :
            return user
    return None






@app.route("/dashboard")
def dashboard() :
    print(session)
    if session.get("username") is not None :
        return render_template("views/dashboard.html")
    return redirect(url_for('login'))


@app.route("/logout")
def logout() :
    session.pop('username', None)
    return redirect(url_for('index'))



###################
#    RECHERCHE    #
###################

@app.route("/recherche")
def recherche() :
    return render_template("views/recherche.html")


###################
#    RECHERCHE    #
###################

@app.route("/partenaires")
def partenaires() :
    return render_template("views/partenaires.html")



# _________________________________________________
#                   LEGAL                    
# _________________________________________________
