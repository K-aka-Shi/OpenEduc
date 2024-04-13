from flask import Flask, abort, render_template, url_for, redirect, flash, request, session
from dotenv import load_dotenv
import os
from db_requetes import *


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}


@app.route("/")
def index():
    return render_template("views/index.html")

# ############################################################################
#                                   NAVIGATION                    
# ############################################################################

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
            session["id"] = utilisateur[0]
            session["username"] = utilisateur[1]
            session["statut"] = utilisateur[3]
            print(session.get("id"), session.get("username"), session.get("statut"))
            flash("Connexion réussie","success")
            return redirect(url_for('dashboard'))
        else :
            print("utilisateur inconnu")
            return redirect(request.url)
    else :
        return render_template("views/login.html")

@app.route("/logout")
def logout() :
    print(session)
    session.pop('username', None)
    session.pop('statut', None)
    return redirect(url_for('index'))


# ############################################################################
#                                   DASHBOARD                    
# ############################################################################

@app.route("/dashboard")
def dashboard() :
    username = session.get("username")
    statut = session.get("statut")
    if username is not None :
        if statut == 1 :
            ecoles = chercher_ecole_formCreerReferent()
            logs = chercher_historiquemodification()
            print(ecoles)
            return render_template("views/dashboard.html",
                               isAdmin=statut,
                               ecoles = ecoles,
                               logs = logs)
        else :
            conn = sqlite3.connect(bdd_name).cursor().execute('SELECT SUM(Effectif) FROM Classe')
            nbEleves = conn.fetchall()[0][0]
            conn = sqlite3.connect(bdd_name).cursor().execute('SELECT COUNT(Effectif) FROM Classe')
            moyenneEleveParClasse = conn.fetchall()[0][0]
            moyenneEleveParClasse = round( nbEleves / moyenneEleveParClasse ,1)
            conn.close()
            return render_template("views/dashboard.html",
                               isAdmin  = statut,
                               nbEleves = nbEleves,
                               moyenneEleveParClasse = moyenneEleveParClasse)
        return render_template("views/dashboard.html",
                               isAdmin=statut)
    return redirect(url_for('login'))



###################
#    REFERENT     #
###################

#    DASHBOARD : Créer Referent    #
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
                flash(f'Le referent a bien été ajouté avec le mot de passe : {newPassword}')
                return render_template("views/dashboard/adminAddRef.html",
                                isAdmin=statut,
                                password = newPassword,
                                ecoles=ecoles
                                )
            return render_template("views/dashboard.html",
                                isAdmin=statut)
        return redirect(url_for('login'))
    else :
        return render_template("views/dashboard/adminAddRef.html",
                               ecoles=ecoles)

#    DASHBOARD : Rechercher Referent    #
# @app.route('/recherche_referents', methods=['POST'])
# def recherche_referents():
#     term = request.form['term']
#     # Utilisez le terme pour effectuer la recherche dans la base de données
#     results = chercher_utilisateurLike(term)
#     print(results)
#     # Renvoyez les résultats à la page HTML
#     return render_template('views/dashboard/adminDeleteRef.html',
#                            isAdmin=session.get("statut"),
#                            referents=results
#                            )

@app.route("/dashboard/rechercher-referent", methods=["POST", "GET"])
def dashboardAdminSearchRef() :
    if request.method == "POST":
        # si le formulaire est envoyé
        data = request.form
        saisie = data.get('query')
        resultats = chercher_utilisateurLike(saisie)
        return render_template("views/dashboard/adminSearchRef.html", resultats=resultats)
    else:
        # méthode GET
        return render_template("views/dashboard/adminSearchRef.html", resultats=None)

#    DASHBOARD : Modifier Referent    #
@app.route("/dashboard/modifier-referent")
def dashboardAdminEditRef() :
    ecoles = chercher_ecoleAll()
    ecoles = sorted(ecoles, key=lambda x: x[2])
    users = chercher_utilisateurAll()
    users = users[1:]
    return render_template("views/dashboard/adminEditRef.html", ecoles=ecoles, utilisateurs=users)

@app.route('/modifier_referent', methods=['POST'])
def modifier_referent():
    data  = request.form
    id_utilisateur = data.get('id_utilisateur')
    identifiant = data.get( 'identifiant' )
    mdp = data.get( 'mdp' )
    idEcole = data.get( 'ecoles' )
    update_referent(id_utilisateur,identifiant,mdp,idEcole)
    return redirect(url_for('dashboardAdminEditRef'))

#    DASHBOARD : Supprimer Referent    #
@app.route("/dashboard/supprimer-referent", methods=['POST', 'GET'])
def dashboardAdminDeleteRef() :
    if request.method == "POST":
        # si le formulaire est envoyé
        data = request.form
        saisie = data.get('term')
        resultats = chercher_utilisateurLike(saisie)
        return render_template("views/dashboard/adminDeleteRef.html", referents=resultats)
    else:
        # méthode GET
        resultats = None
        return render_template("views/dashboard/adminDeleteRef.html", referents=resultats)

@app.route('/supprimer_referents', methods=['POST'])
def supprimer_referents():
    # referents_a_supprimer = request.form.getlist('referents')
    referents_a_supprimer = request.form.getlist('referent_id')
    print("referent a supp",referents_a_supprimer)
    # Effectuer les opérations de suppression dans la base de données
    supprimer_utilisateurByID(referents_a_supprimer)
    # Rediriger vers une page de confirmation ou de retour à la page d'accueil
    return render_template("views/dashboard/adminDeleteRef.html")


###################
#    ECOLES       #
###################

#    DASHBOARD : Créer Ecole    #
@app.route("/dashboard/creer-ecole", methods=["POST", "GET"])
def dashboardAdminAddEcole() :
    username = session.get("username")
    statut = session.get("statut")
    if request.method == 'POST' :
        data = request.form
        nom           = data.get("nomEcole")
        adresse       = data.get("adresse")
        ville         = data.get("ville")
        codePostal    = data.get("codePostal")
        cycleScolaire = data.get("cycleScolaire")
        inserer_ecole(nom,adresse,ville,codePostal,cycleScolaire)
        print(chercher_ecole_testVerifAdd(nom,adresse,ville,codePostal,cycleScolaire))
        flash("Ecole crée !", category='success')  # Affichage du message de succes
        return render_template("views/dashboard/adminAddEcole.html", resultats=None)
    else :
        if username is not None and statut == 1 :
            return render_template("views/dashboard/adminAddEcole.html", resultats=None)
        return redirect(request.url)

#    DASHBOARD : Rechercher Ecole    #
@app.route('/recherche_ecole', methods=['POST'])
def recherche_ecole():
    return render_template('views/dashboard/adminDeleteEcole.html')

@app.route("/dashboard/rechercher-ecole", methods=["POST", "GET"])
def dashboardAdminSearchEcole() :
    if request.method == "POST" :
        data = request.form
        saisie = data.get('query')
        resultats = chercher_ecoleLike(saisie)
        print("saisie :",saisie, "\n Résultats :\n", resultats)
        return render_template("views/dashboard/adminSearchEcole.html", resultats=resultats)
    else :
        # méthode GET
        return render_template("views/dashboard/adminSearchEcole.html", resultats=None)

#    DASHBOARD : Modifier Ecole    #
@app.route("/dashboard/modifier-ecole")
def dashboardAdminEditEcole() :
    ecoles = chercher_ecoleAll()
    ecoles = sorted(ecoles, key=lambda x: x[2])
    return render_template("views/dashboard/adminEditEcole.html", ecoles=ecoles)

@app.route('/modifier_ecole', methods=['POST'])
def modifier_ecole():
    data = request.form
    id_ecole = data.get('id_ecole')
    nomEcole = data.get('nomEcole')
    adresse = data.get('adresse')
    ville = data.get('ville')
    codePostal = data.get('codePostal')
    nbEleves = data.get('nbEleves')
    telephone = data.get('telephone')
    email = data.get('email')
    cycleScolaire = data.get('cycleScolaire')
    update_ecole(id_ecole, nomEcole, adresse, ville, codePostal, nbEleves, telephone, email, cycleScolaire)

    return redirect(url_for('dashboardAdminEditEcole'))

#    DASHBOARD : Supprimer Ecole    #
@app.route("/dashboard/supprimer-ecole", methods=['POST', 'GET'])
def dashboardAdminDeleteEcole() :
    if request.method == "POST":
        # si le formulaire est envoyé
        data = request.form
        saisie = data.get('term')
        resultats = chercher_ecoleLike(saisie)
        return render_template("views/dashboard/adminDeleteEcole.html", ecoles=resultats)
    else:
        # méthode GET
        resultats = None
        return render_template("views/dashboard/adminDeleteEcole.html", ecoles=resultats)

@app.route('/supprimer_ecole', methods=['POST'])
def supprimer_ecole():
    ecoles_a_supprimer = request.form.getlist('ecole_id')
    print(ecoles_a_supprimer)
    # Effectuer les opérations de suppression dans la base de données
    supprimer_ecoleByID(ecoles_a_supprimer)
    # Rediriger vers une page de confirmation ou de retour à la page d'accueil
    return render_template("views/dashboard/adminDeleteEcole.html")


#############################
#    DASHBOARD REFERENTS    #
#############################

@app.route("/dashboard/ecole", methods=["POST", "GET"])
def referentEcole() :
    username = session.get("username")
    statut = session.get("statut")
    id = session.get('id')
    if request.method == "POST":
        # si le formulaire est envoyé
        conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                        SELECT Ecole.idEcole
                                                        FROM Ecole, Utilisateur
                                                        WHERE Ecole.idEcole = Utilisateur.idEcole AND idUtilisateur=?
                                                        """, (id,) )
        MonEcoleID = conn.fetchall()[0][0]
        print(MonEcoleID)
        data = request.form
        nomEcole = data.get('nom_ecole')
        adresse = data.get('adresse')
        ville = data.get('ville')
        codePostal = data.get('codePostal')
        telephone = data.get('telephone')
        email = data.get('email')
        cycleScolaire = data.get('cycleScolaire')
        update_ecole(MonEcoleID, nomEcole, adresse, ville, codePostal, None, telephone, email, cycleScolaire)
        return redirect(request.url)
    else:
        # méthode GET
        if username is not None and statut == 0 :
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                            SELECT Ecole.idEcole, nomEcole, Adresse, Ville, CodePostal, nbEleves, Telephone, Email, cycleScolaire
                                                            FROM Ecole, Utilisateur WHERE Ecole.idEcole = Utilisateur.idEcole AND idUtilisateur=?
                                                            """, (id,) )
            monEcole = conn.fetchall()[0]
            conn = sqlite3.connect(bdd_name).cursor().execute('SELECT SUM(Effectif) FROM Classe')
            nbEleves = conn.fetchall()[0][0]
            conn.close()
            return render_template("views/dashboard/referentEcole.html",
                                monEcole = monEcole,
                                nbEleves = nbEleves)
        return redirect(url_for('dashboard'))



@app.route("/dashboard/classe", methods=["POST", "GET"])
def referentClasse() :
    username = session.get("username")
    statut = session.get("statut")
    id = session.get("id")
    print('session', id)
    if request.method == "POST":
        # si le formulaire est envoyé
        submit_type = request.form.get('submit-type')
        if submit_type == 'Ajouter':
            # Traitement pour le formulaire d'ajout
            print("\n\nTraitement pour le formulaire d'ajout\n\n")
            data = request.form
            niveauScolaire = data.get('niveau')
            prof = data.get('nom_prof')
            effectif = data.get('effectifs')
            moyenne = data.get('moyenne')
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                              SELECT idEcole, nomEcole 
                                                              FROM Ecole
                                                              WHERE idEcole = (
                                                                    SELECT idEcole
                                                                    FROM Utilisateur
                                                                    WHERE idUtilisateur = ?
                                                                )""",
                                                              (id,)
                                                            )
            idEcole = conn.fetchall()[0]
            print(session)
            print("formulaire ajouter classe :", prof, effectif, niveauScolaire, idEcole[1])
            inserer_classe(effectif, moyenne, niveauScolaire, prof, idEcole[0])
        elif submit_type == 'Modifier':
            # Traitement pour le formulaire de modification
            print("\n\nTraitement pour le formulaire de modification\n\n")
        return redirect(request.url)
    else :
        # méthode GET
        if username is not None and statut == 0 :
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                              SELECT cycleScolaire
                                                              FROM Ecole, Utilisateur
                                                              WHERE Ecole.idEcole = Utilisateur.idEcole
                                                                AND idUtilisateur=?""", (id,)
                                                            )
            cycleScolaire = conn.fetchall()[0][0]
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                              SELECT c.niveauScolaire, p.Nom, p.Prenom, c.Effectif, c.Moyenne
                                                              FROM Classe c
                                                              JOIN Personnel p ON c.idPersonnel = p.idPersonnel
                                                              JOIN Utilisateur u ON c.idEcole = u.idEcole
                                                              WHERE u.idUtilisateur = ?""", (id,)
                                                              )
            classes = conn.fetchall()
            print(classes)
            print(cycleScolaire, classes)
            conn.close()
            return render_template("views/dashboard/referentClasse.html",
                                   cycleScolaire = cycleScolaire,
                                   classes = classes)
        return redirect(url_for('dashboard'))


@app.route("/dashboard/personnels", methods=["POST", "GET"])
def referentPersonnels() :
    if request.method == "POST":
        # si le formulaire est envoyé
        # data = request.form
        # saisie = data.get('term')
        # resultats = chercher_ecoleLike(saisie)
        return render_template("views/dashboard/referentPersonnel.html")
    else:
        # méthode GET
        return render_template("views/dashboard/referentPersonnel.html")


# ############################################################################
#                                   RECHERCHER UNE ECOLE                    
# ############################################################################

@app.route("/recherche", methods=["POST", "GET"])
def recherche() :
    if request.method == "POST":
        # si le formulaire est envoyé
        data = request.form
        saisie = data.get('query')
        print("Saisie :",saisie)
        resultats = chercher_ecole(saisie)
        # tab = [res for res in resultats]
        # print(tab)
        # resultats = [1:]
        print(resultats)
        return render_template("views/recherche.html", resultats=resultats)
    else :
        # méthode GET
        resultats = None
        return render_template("views/recherche.html", resultats=resultats)
    # print("ECOLES RECHERCHE ALL")
    # q = request.args.get('query')
    # print("\nQ :",q)
    # if q :
    #     results = chercher_ecoleAll()
    #     print("\nresults :\n",results)
    # else :
    #     results = []
    # return render_template("views/recherche.html")




###################
#   PARTENAIRES   #
###################

@app.route("/partenaires")
def partenaires() :
    ecoles = chercher_ecoleAll()
    print("\n\nECOLES :\n",ecoles[0], '\n\n')
    ecoles = sorted(ecoles, key=lambda x: x[2])
    for ecole in ecoles :
        print(ecole[2], ecole[0])
    return render_template("views/partenaires.html",  ecoles=ecoles)



# ############################################################################
#                                   LEGAL                    
# ############################################################################


@app.route("/protection-des-donnees")
def protectionDesDonnees() :
    return render_template("views/legal/protection-des-donnees.html")


@app.route("/mentions-legales")
def mentionsLegales() :
    return render_template("views/legal/mentions-legales.html")


@app.route("/cgu")
def cgu() :
    return render_template("views/legal/cgu.html")




# ############################################################################
#                                   ERREURS                    
# ############################################################################

# Forbidden
@app.errorhandler(403)
def not_found(e):
  return render_template('views/error/403.html'), 403

# Page not found
@app.errorhandler(404)
def not_found(e):
  return render_template('views/error/404.html'), 404

# Page not allowed
@app.errorhandler(405)
def not_found(e):
  return render_template('views/error/405.html'), 405

# Internal Server Error
@app.errorhandler(500)
def not_found(e):
  return render_template('views/error/500.html'), 500
