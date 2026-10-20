# **PROGRAMMATION PYTHON - SEANCE 1**


Initialisation du projet de web scraping,

On va utliser selenium et nom bs4 et request car il est limité pour des sites web qui sont genere dynamiquement.

On doit maitriser les selecteurs CSS, on doit pouvoir manipuler des fichier CSV 

Les données seront mises dans un CSV puis dans une BD SQLite, 

Il faudrait lire la 'documentation' du site a scraper, 

On ne scrape pas des données à caracteres personelles, uniquement des donées comme : le nom le prix l'image, la description

Il faut tenir compte de la pagination

Il utilise un webdriver firefox / chrome
Il est important d'ajouter des timeout



La demarche a suivre :
Concevoir un programme python pour faire une analys



Les données à scrapper sont de la catégorie technologies



La base c'est un application console si on decide de faire une interface graphique

les image doivent aussi etre recupent (je pensque que ce sera le lien de l'image hein)

dossier data -> dossier tech -> ecouteurs -> data.csv & images (image 1.png)
et à la racine du dossier data on a un fichier recap.csv pour dire combien de categories on a scraper

On est dans une architechture MVC


FONCTIONNALITEES A IMPLEMENTER :
* Interface
* Recuperztion de l'image du produit
* Filtre pour filitrer certains produits de marque comme "iphone" et n'avoir que des iphone, 
* Des statistiques pour une étude de marché
* La pagination




dossier app 
    dossier conttrolers 
        init.py
        scrappingcontroller.py
    dossier models
        init.py
        depot.py
        produit.py
    dossier scrapper
    views
        init.py
        consoleview.py
        exportview
dossier data



Le versionning :
v1.2.3 (majeure.intermediare.mineur)


revision sur Git/Git Hub