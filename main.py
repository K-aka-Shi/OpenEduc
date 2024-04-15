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
        submit_type = request.form.get('submit-generate')
        print("SUBMIT_TYPE", submit_type)
        # Formulaire Regénérer mdp
        if submit_type == "Regénérer":
            id_utilisateur = request.form.get('idUtilisateur')
            user = chercher_utilisateurByID(id_utilisateur)
            if user != [] :
                user = user[0]
                if user[3] == 0 :
                    update_mdpUtilisateur_byID(id_utilisateur)
                    flash(f"""Mot de passe regénéré de l'utilisateur {user[1]}. Mot de passe : {chercher_utilisateurByID(id_utilisateur)[0][2]}""")
            return redirect(request.url)
        else :
            data = request.form
            saisie = data.get('query')
            resultats = chercher_utilisateurLike(saisie)
            print('final',resultats)
            return render_template("views/dashboard/adminSearchRef.html", resultats=resultats)
    else:
        # méthode GET
        return render_template("views/dashboard/adminSearchRef.html", resultats=None, newPassword=None)

#    DASHBOARD : Modifier Referent    #
@app.route("/dashboard/modifier-referent", methods=["POST", "GET"])
def dashboardAdminEditRef() :
    username = session.get("username")
    statut = session.get("statut")
    id = session.get('id')
    ecoles = sorted(chercher_ecoleAll(), key=lambda x: x[3]) # Toutes les écoles par ville triées par ordre alph.
    users = chercher_utilisateurAll()[1:]

    if request.method == "POST":

        submit_type = request.form.get('submit-type')
        print("submit",submit_type)
        data = request.form

        if submit_type == "Rechercher" :
            id_utilisateur = data.get('id_utilisateur')
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                        SELECT idUtilisateur,Identifiant, MotDePasse, idEcole
                                                        FROM Utilisateur WHERE idUtilisateur = ?
                                                            """, (id_utilisateur,) )
            Utilisateur = conn.fetchall()[0]
            # pour le selecteur des utilisateur
            id_utilisateur = Utilisateur[0]
            identifiant = Utilisateur[1]
            mdp = Utilisateur[2]
            ecole = Utilisateur[3]
            print(ecole)
            print(ecoles)
            return render_template("views/dashboard/adminEditRef.html",
                                   utilisateurs=users, ecoles=ecoles, affichage=True,
                                   id_utilisateur=id_utilisateur,identifiant=identifiant, mdp=mdp, ecole=ecole)
        
        if submit_type == "Modifier" :

            id_utilisateur = data.get('id_utilisateur')
            print(id_utilisateur)
            NVidentifiant = data.get('identifiant')
            NVmdp = data.get('mdp')
            NVecole = data.get('ecoles')
            update_referent(id_utilisateur, NVidentifiant, NVmdp, NVecole)
            print("chercher",chercher_utilisateur(NVidentifiant,NVmdp))
            return render_template("views/dashboard/adminEditRef.html",
                                   utilisateurs=users,
                                   id_utilisateur=id_utilisateur,identifiant=NVidentifiant, mdp=NVmdp, ecole=NVecole, ecoles=ecoles)
    else :
        # GET
        if username is not None and statut == 1 :
            ecoles = chercher_ecoleAll()
            return render_template("views/dashboard/adminEditRef.html",
                                ecoles = ecoles, utilisateurs=users)
        return redirect(url_for('dashboard'))


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
@app.route("/dashboard/modifier-ecole", methods=["POST","GET"])
def dashboardAdminEditEcole() :
    username = session.get("username")
    statut = session.get("statut")
    id = session.get('id')
    ecoles = sorted(chercher_ecoleAll(), key=lambda x: x[3]) # Toutes les écoles par ville triées par ordre alph.
    users = chercher_utilisateurAll()[1:]

    if request.method == "POST":

        submit_type = request.form.get('submit-type')
        print("submit",submit_type)
        data = request.form

        if submit_type == "Rechercher" :
            id_ecole = data.get('id_ecole')
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                        SELECT *
                                                        FROM Ecole
                                                        WHERE idEcole = ?
                                                            """, (id_ecole,) )
            Ecole = conn.fetchall()[0]
            print("aaaaaaaaaaaa",Ecole)
            # pour le selecteur des utilisateur
            id_ecole = Ecole[0]
            nomEcole = Ecole[1]
            adresse = Ecole[2]
            ville = Ecole[3]
            codePostal = Ecole[4]
            nbEleves = Ecole[5]
            telephone = Ecole[6]
            email = Ecole[7]
            cycleScolaire = Ecole[8]
            print(ecoles)
            return render_template("views/dashboard/adminEditEcole.html",
                                   utilisateurs=users, ecoles=ecoles, affichage=True, monEcole=Ecole,
                                   id_ecole=id_ecole, nomEcole=nomEcole, adresse=adresse,
                                   ville=ville, codePostal=codePostal, nbEleves=nbEleves, telephone=telephone, email=email, cycleScolaire=cycleScolaire
                                   )

        if submit_type == "Modifier" :

            id_ecole = data.get('id_ecole')
            print(id_ecole)
            nomEcole = data.get('nomEcole')
            adresse = data.get('adresse')
            ville = data.get('ville')
            codePostal = data.get('codePostal')
            nbEleves = data.get('nbEleves')
            telephone = data.get('telephone')
            email = data.get('email')
            cycleScolaire = data.get('cycleScolaire')
            update_ecole(id_ecole, nomEcole, adresse, ville, codePostal, nbEleves, telephone, email, cycleScolaire)
            print("chercher",chercher_ecole_testVerifAdd(nomEcole, adresse, ville, codePostal))
            return render_template("views/dashboard/adminEditEcole.html",
                                   utilisateurs=users,
                                   ville=ville, codePostal=codePostal, nbEleves=nbEleves, telephone=telephone, email=email, cycleScolaire=cycleScolaire
                                    )

    else :
        # GET
        if username is not None and statut == 1 :
            ecoles = chercher_ecoleAll()
            return render_template("views/dashboard/adminEditEcole.html",
                                ecoles = ecoles, utilisateurs=users)
        return redirect(url_for('dashboard'))



    ecoles = chercher_ecoleAll()
    ecoles = sorted(ecoles, key=lambda x: x[2])
    return render_template("views/dashboard/adminEditEcole.html", ecoles=ecoles)

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
    monEcole = chercher_monEcole(id)
    print("monecole",monEcole)

    if request.method == "POST":

        # si le formulaire est envoyé
        submit_type = request.form.get('submit-type')
        
        if submit_type == 'Ajouter':

            # Traitement pour le formulaire d'ajout
            print("\n\n AJOUT CLASSE \n\n")
            data = request.form
            niveauScolaire = data.get('niveau')
            prof = data.get('nom_prof')
            effectif = data.get('effectifs')
            moyenne = data.get('moyenne')

            inserer_classe(effectif, moyenne, niveauScolaire, prof, monEcole)

            return redirect(request.url)

        elif submit_type == 'Modifier' :
            print("\n\n MODIFICATION CLASSE \n\n")

            data = request.form
            idClasse = data.get('idClasse')
            niveauScolaire = data.get('niveau')
            prof = data.get('nom_prof')
            effectif = data.get('effectifs')
            moyenne = data.get('moyenne')

            update_classe(idClasse,niveauScolaire,prof,effectif,moyenne)

            return redirect(request.url)
    
        elif submit_type == 'Supprimer':
            print("\n\n SUPPRESSION CLASSE \n\n")

            data = request.form
            idClasse = data.getlist('idClasse')
            print("idClasse",idClasse)

            supprimer_classe(idClasse)

            return redirect(request.url)

    else :
        # méthode GET
        if username is not None and statut == 0 :
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                              SELECT cycleScolaire
                                                              FROM Ecole, Utilisateur
                                                              WHERE Ecole.idEcole = Utilisateur.idEcole
                                                                AND idUtilisateur = ?""", (id,)
                                                            )
            cycleScolaire = conn.fetchall()[0][0]
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                              SELECT c.idClasse, c.niveauScolaire, p.Nom, p.Prenom, c.Effectif, c.Moyenne
                                                              FROM Classe c
                                                              JOIN Personnel p ON c.idPersonnel = p.idPersonnel
                                                              JOIN Utilisateur u ON c.idEcole = u.idEcole
                                                              WHERE u.idUtilisateur = ?""", (id,)
                                                              )
            classes = conn.fetchall()
            conn.close()
            return render_template("views/dashboard/referentClasse.html",
                                   cycleScolaire = cycleScolaire,
                                   classes = classes,
                                   profs = chercher_profs(monEcole)
                                   )
        return redirect(url_for('dashboard'))


@app.route("/dashboard/personnel", methods=["POST", "GET"])
def referentPersonnel() :
    username = session.get("username")
    statut = session.get("statut")
    id = session.get("id")
    monEcole = chercher_monEcole(id)

    if request.method == "POST":

        # si le formulaire est envoyé
        submit_type = request.form.get('submit-type')
        data = request.form

        if submit_type == "Rechercher" :
            idPersonnel = data.get('idPersonnel')
            conn = sqlite3.connect(bdd_name).cursor().execute("""SELECT * FROM Personnel WHERE idPersonnel = ?
                                                              """, (idPersonnel,) )
            Personnel = conn.fetchall()[0]
            print(Personnel)
            print("aaaaaaaaaaaa",Personnel)
            # pour le selecteur des utilisateur
            data = request.form
            sexe = Personnel[3]
            nomPersonnel = Personnel[1]
            prenomPersonnel = Personnel[2]
            telephone = Personnel[4]
            email = Personnel[5]
            fonction = Personnel[6]

            print(Personnel)

            conn = sqlite3.connect(bdd_name).cursor().execute("""SELECT cycleScolaire FROM Ecole, Utilisateur WHERE Ecole.idEcole = Utilisateur.idEcole AND idUtilisateur = ?""", (id,))
            cycleScolaire = conn.fetchall()[0][0]
            conn = sqlite3.connect(bdd_name).cursor().execute("""SELECT idPersonnel, Nom, Prenom, Sexe, Telephone, Email, Fonction, idClasse FROM Personnel p JOIN Utilisateur u ON p.idEcole = u.idEcole WHERE p.idEcole = ?""", (monEcole,))
            personnels = conn.fetchall()
            conn.close()

            return render_template("views/dashboard/referentPersonnel.html",
                                   cycleScolaire = cycleScolaire, personnels = personnels, profs = chercher_profs(monEcole),
                                   affichage=True,
                                   idPersonnel=idPersonnel, sexe=sexe, nomPersonnel=nomPersonnel, prenomPersonnel=prenomPersonnel, telephone=telephone, email=email, fonction=fonction
                                   )

        
        if submit_type == 'Ajouter':

            # Traitement pour le formulaire d'ajout
            print("\n\n AJOUT PERSONNEL \n\n")

            sexe = data.get('sexe')
            nomPersonnel = data.get('nomPersonnel')
            prenomPersonnel = data.get('prenomPersonnel')
            telephone = data.get('telephone')
            email = data.get('email')
            fonction = data.get('fonction')
        
            inserer_personnel(nomPersonnel, prenomPersonnel, sexe, telephone, email, fonction, monEcole)

            return redirect(request.url)

        if submit_type == 'Modifier' :
            print("\n\n MODIFICATION PERSONNEL \n\n")

            idPersonnel = data.get('idPersonnel')
            sexe = data.get('sexe')
            nomPersonnel = data.get('nomPersonnel')
            prenomPersonnel = data.get('prenomPersonnel')
            telephone = data.get('telephone')
            email = data.get('email')
            fonction = data.get('fonction')

            update_personnel(idPersonnel, sexe, nomPersonnel, prenomPersonnel, telephone, email, fonction)

            return redirect(request.url)
    
        if submit_type == 'Supprimer':
            print("\n\n SUPPRESSION PERSONNEL \n\n")

            idPersonnel = data.getlist('idPersonnel')
            print("idpersonnel",idPersonnel)

            supprimer_personnel(idPersonnel)

            return redirect(request.url)

    else :
        # méthode GET
        if username is not None and statut == 0 :
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                              SELECT cycleScolaire
                                                              FROM Ecole, Utilisateur
                                                              WHERE Ecole.idEcole = Utilisateur.idEcole
                                                                AND idUtilisateur = ?""", (id,)
                                                            )
            cycleScolaire = conn.fetchall()[0][0]
            conn = sqlite3.connect(bdd_name).cursor().execute("""
                                                    SELECT idPersonnel, Nom, Prenom, Sexe, Telephone, Email, Fonction, idClasse
                                                    FROM Personnel p
                                                    JOIN Utilisateur u ON p.idEcole = u.idEcole
                                                    WHERE p.idEcole = ?""", (monEcole,)
                                                              )
            personnels = conn.fetchall()
            conn.close()
            return render_template("views/dashboard/referentPersonnel.html",
                                   cycleScolaire = cycleScolaire,
                                   personnels = personnels,
                                   profs = chercher_profs(monEcole)
                                   )
        return redirect(url_for('dashboard'))


# ############################################################################
#                          RECHERCHER UNE ECOLE                    
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
