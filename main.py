from flask import Flask, render_template, url_for, redirect, request, session
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
            print(utilisateur)
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
        return render_template("views/dashboard.html",
                               isAdmin=statut)
    return redirect(url_for('login'))

# Ajouter
@app.route("/dashboard/creer-referent", methods=["POST", "GET"])
def dashboardAdminAddRef() :
    ecoles = chercher_ecole_formCreerReferent()
    if request.method == "POST" :
        username = session.get("username")
        statut = session.get("statut")
        if username is not None :
            if statut == 1 :
                data = request.form
                identifiant = data.get("identifiant")
                idEcole = data.get("idEcole")
                newPassword = inserer_referent(identifiant,idEcole)
                return render_template("views/dashboard/adminAddRef.html",
                                isAdmin=statut,
                                password = newPassword
                                )
            return render_template("views/dashboard.html",
                                isAdmin=statut)
        return redirect(url_for('login'))
    else :
        return render_template("views/dashboard/adminAddRef.html",
                               ecoles=ecoles)

# Rechercher
@app.route('/recherche_referents', methods=['POST'])
def recherche_referents():
    term = request.form['term']
    # Utilisez le terme pour effectuer la recherche dans la base de données
    results = chercher_utilisateurLike(term)
    print(results)
    # Renvoyez les résultats à la page HTML
    return render_template('views/dashboard/adminDeleteRef.html',
                           isAdmin=session.get("statut"),
                           referents=results
                           )

@app.route('/supprimer_referents', methods=['POST'])
def supprimer_referents():
    referents_a_supprimer = request.form.getlist('referents')
    print("referent a supp",referents_a_supprimer)
    # Effectuer les opérations de suppression dans la base de données
    supprimer_utilisateurByID(referents_a_supprimer)
    # Rediriger vers une page de confirmation ou de retour à la page d'accueil
    return redirect(url_for('dashboardAdminDeleteRef'))

@app.route("/dashboard/rechercher-referent")
def dashboardAdminSearchRef() :
    return render_template("views/dashboard/adminSearchRef.html")

@app.route("/dashboard/modifier-referent")
def dashboardAdminEditRef() :
    return render_template("views/dashboard/adminEditRef.html")

@app.route("/dashboard/supprimer-referent")
def dashboardAdminDeleteRef() :
    return render_template("views/dashboard/adminDeleteRef.html")



###################
#    RECHERCHE    #
###################

@app.route("/recherche")
def recherche() :
    # if request.method == "POST":
    #     # si le formulaire est envoyé
    #     data = request.form
    #     saisie = data.get('query')
    #     print("Saisie :",saisie)
    #     resultats = chercher_ecoleAll()
    #     tab = [res for res in resultats]
    #     print(tab)
    #     # resultats = [1:]
    #     print(resultats)
    # else:
        # méthode GET
        # resultats = None
    # return render_template("views/recherche.html", resultats=tab)
    print("ECOLES RECHERCHE ALL")
    q = request.args.get('query')
    print("\nQ :\n",q)
    if q :
        results = chercher_ecoleAll()
        print("\nresults :\n",results)
    else :
        results = []
    return render_template("views/recherche.html", resultats=results)



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




# _________________________________________________
#                   ERREURS                    
# _________________________________________________

# Page not found
@app.errorhandler(404)
def not_found(e):
  return render_template('error404.html'), 404

# Page not allowed
@app.errorhandler(405)
def not_found(e):
  return render_template('error404.html'), 405


