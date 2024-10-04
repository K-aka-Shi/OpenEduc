[![Typing SVG](https://readme-typing-svg.demolab.com?font=Schoolbell&size=60&duration=10000&pause=2000&color=F9A825&background=0A4191&center=true&vCenter=true&width=1000&height=200&lines=OpenEduc)](https://git.io/typing-svg)

OpenEduc est un projet développé dans le cadre du BTS Services Informatiques aux Organisations (SIO) pour l'épreuve E5 - Conception et développement d'applications.

## Description

OpenEduc est une plateforme web conçue pour faciliter la collecte et la diffusion d'informations sur les écoles. L'objectif principal est de permettre aux référents locaux de saisir en ligne les informations relatives à une école, simplifiant ainsi le processus actuel basé sur l'envoi de fichiers.

## Fonctionnalités

- Ajout, modification et suppression des référents locaux.
- Recherche d'écoles par ID.
- Affichage des détails des écoles.
- Gestion des utilisateurs (administrateurs et référents locaux).
- etc.

## Technologies utilisées

| **Outil**         | **Utilité**     |
| :---: | --- |
| `Flask`           | *Framework web en Python pour le back-end.* |
| `HTML/CSS/JS`     | *Langages de développement web pour le front-end.* |
| `SQLite`          | *Système de gestion de base de données relationnelle.* |
| `Git`             | *Système de contrôle de version pour la collaboration et le suivi des modifications.* |
| `GitHub`          | *Plateforme d'hébergement et de gestion de code source.* |

## Installation et utilisation

1. Cloner le dépôt : 
    ```sh
    git clone "https://github.com/votre-utilisateur/OpenEduc.git"
   ```
2. Configurer les variables d'environnement dans un fichier `.env`.
    ```python
    APP_SECRET_KEY= "inventer une clé"
    ```
3. Mettre en place l'environnement virtuel
    ```sh
    python -m venv venv
    ```
    ```sh
    . venv\Scripts\activate
    ```
4. Installer les dépendances :
    ```sh
    pip install -r requirements.txt
    ```

5. Lancer l'application :
    ```sh
    python main.py
    ```
    ou
    ```sh
    flask --app main run --debug
    ```

## Contributeurs

- [K_aka_Shi](https://github.com/K-aka-Shi)

## Licence

Ce projet est distribué sous la licence [MIT](https://opensource.org/licenses/MIT)
