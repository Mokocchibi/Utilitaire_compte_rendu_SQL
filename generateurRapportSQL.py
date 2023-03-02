import configparser
import pysftp
from pysftp import CnOpts
import re

config = configparser.ConfigParser()
config.read('config.ini')

host = config['SFTP']['host']
username = config['SFTP']['username']
password = config['SFTP']['password']

cnopts = CnOpts()
cnopts.hostkeys = None

procedures = []
packages = []
triggers = []
tables = []

corresDefNomFichier = {
    "AjoutCommande.sql": "Cette prodécure permet d'ajouter un produit dans une commande d'un client avec ses attributs.",
    "AjoutPanier.sql": "Cette procédure ajoute un produit dans le panier d'un client. Le panier est créé s'il n'existe pas sinon le produit y est directement ajouté.",
    "AjouterDansCategorie.sql": "Cette procédure ajoute un produit dans une catégorie s'il n'y est pas déjà. La procédure est réservé aux administrateurs.",
    "CategorieFromProduct.sql": "Cette procédure créer une table temporaire contenant tous les identifiants des catégories du produit donné en paramètre afin de les récupérer dans le code après.",
    "CreerPanier.sql": "Cette procédure permet de créer un panier appartenant à un client.",
    "CreerProduit.sql": "Cette procédure permets de créer un produit, elle est révervé aux administrateurs.",
    "ProduitsFromCategorie.sql": "Cette procédure récupère tous les produits d'une catégorie via une table temporaire qui sera utilisé plus tard dans le code.",
    "ProduitsFromPanier.sql": "Cette procédure récupère les produits d'un panier d'un client en les insérant dans une table temporaire qui sera utilisé plus tard dans le code.",
    "ProduitsFromSearchTerme.sql": "Cette procédure récupère les produits contenant le paramètre \"le_searchterm\" dans son nom ou sa description et les produits qui n'on pas déjà été ajouté qui ont une catégorie qui contient \"le_searchterm\" dans son nom, sa description ou son theme.",
    "TiggerStockQte.sql": "Ce trigger vérifie avant l'ajout d'un produit dans la commande d'un client si la quantité choisis de produits est supérieure au stock disponible.",
    "TriggerAjoutProduitCommande.sql": "Ce trigger mets à jour la commande d'un client après qu'il y ait ajouté un article.",
    "TriggerAjoutProduitPanier.sql": "Ce trigger mets à jour le panier d'un client après qu'il y ait ajouté un article.",
    "TriggerDelPanier.sql": "Ce trigger supprime les produits des tables liés au panier après suppression dans ce dernier.",
    "TriggerQteStock.sql": "Ce trigger vérifie si la quantité disponible d'un produit est supérieure à la quantité demandé à chaque modification de stock de ce dernier. ",
    "Trigger_Del_product.sql": "Ce trigger supprime les produits dans les tables liés à l a table produit si un produit est supprimé de cette table. Cela mets également à jour les commandes et paniers des clients.",
    "Trigger_del_categorie.sql": "Ce trigger supprime les correspondances entre un produit et une catégorie quand elle est supprimé.",
    "Trigger_del_client.sql": "Ce trigger supprime le panier d'un client quand il est supprimé.",
    "Trigger_del_commande.sql": "Ce trigger supprime un produit de la ligne de commande d'un client quand il le supprime de sa commande.",
    "Trigger_del_panier_de.sql": "Ce trigger supprime le panier dans la table panier quand le panier correspondant dans la table panier_de est supprimé.",
    "create_database.sql": {
        "PRODUCT": [
        "Cette table contient l'ensemble des produits du site.",
            {
            "id (int primary key not null)": "identifiant unique du produit",
            "nom (varchar(25) )": "nom du produit",
            "prixunitaire (decimal(10,2))": "prix unitaire du produit",
            "stocktotal (int)": "stock total disponible du produit",
            "description (text)": "description détaillée du produit",
            "imageurl (varchar(500))": "URL de l'image du produit"
            }
        ],
        "COMMANDE": [
        "Cette table contient les informations sur les commandes passées sur le site.",
            {
            "id (int primary key not null)": "identifiant unique de la commande",
            "prix (decimal(10,2))": "prix total de tous les produits commandés",
            "date_demande (varchar(10))": "date de la commande",
            "adresse_postale (varchar(50))": "adresse postale de livraison de la commande"
            }
        ],
        "LIGNECOMMANDE": [
        "Table est liéé à COMMANDE. Pour chaque produit dans COMMANDE, il existe une LIGNECOMMANDE qui contient les informations sur le produit, comme la quantité de ce-dernier.",
            {
            "id_product (int)": "identifiant unique du produit dans la commande",
            "numcommande (int)": "identifiant (non unique) lié à id de la table COMMANDE",
            "quantite (int)": "quantité du produit incluse dans la commande"
            }
        ],
        "CATEGORIE": [
        "Cette table contient les catégories des produits disponibles sur le site. Un produit peut appartenir a 0, 1 ou plusieurs catégories en même temps.",
            {
            "id (int primary key not null)": "identifiant unique de la catégorie",
            "nom (varchar(20) unique)": "nom de la catégorie",
            "theme (varchar(20))": "thème de la catégorie",
            "description (varchar(100))": "description détaillée de la catégorie"
            }
        ],
        "APPARTIENT": [
            "Tble permet de lier des produits et des catégories.",
            {
                "id_product (int)": "identifiant unique du produit",
                "id_categorie (int)": "identifiant unique de la catégorie"
            }
        ],
        "CLIENT": [
            "La table CLIENT contient les informations sur les clients enregistrés sur le site.",
            {
                "id (int primary key not null)": "Chaque client a un identifiant unique 'id'",
                "email (varchar(50) unique)": "Chaque client a un un email unique 'email'",
                "nom (varchar(20))": "nom du client",
                "prenom (varchar(20))": "prenom du client",
                "motdepasse (varchar(100))": "mot de passe (hashé) du client"
            }
        ],
        "VISITEUR": [   
            "",
            {
                "id (int primary key not null)": "",
                "email (varchar(50) unique)": ""
            }
        ],
        "ADMINISTRATEUR": [
            "La table ADMINISTRATEUR contient les informations sur les administrateurs enregistrés sur le site. Les administateurs sont disctincts des clients, ils ne peuvent pas commander de produits et ne sont pas lier à un panier. Ils ont des accès spéciaux aux pages admin.",
            {
                "id (int primary key not null)": "Chaque administrateur a un identifiant unique 'id'",
                "nom (varchar(20))": "nom de l'admin",
                "prenom (varchar(20))": "prenom de l'admin",
                "motdepasse (varchar(100))": "mot de passe (hashé) de l'admin"
            }
        ],
        "PANIER": [
            "Chaque PANIER est lié à un client",
            {
                "id (int primary key)": "id unique du panier",
                "prix (int)": "prix total des produits contenus dans le panier"
            }
        ],
        "EFFECTUE_PAR_CLIENT": [
            "",
            {
                "id_commande (int)": "",
                "id_client (int)": ""
            }
        ],
        "LIGNEPANIER": [
            "Table est liéé à PANIER. Pour chaque produit dans PANIER, il existe une LIGNEPANIER qui contient les informations sur le produit, comme la quantité de ce-dernier.",
            {
                "id_product (int)": "id unique du produit",
                "id_panier (int)": "id unique du panier, lié à id de PANIER",
                "quantite (int)": "quantité du produit"
            }
        ],
        "PANIER_DE": [
            "Table liant le client à son panier",
            {
                "id_client (int)": "id unique du client",
                "id_panier (int)": "id unique du panier"
            }
        ],
        "PANIER_DE_VIS": [
            "",
            {
                "id_visiteur (int)": "",
                "id_panier (int)": ""
            }
        ],
    }
}

def get_description(nom_fichier):
    if nom_fichier in corresDefNomFichier:
        return corresDefNomFichier[nom_fichier]
    return ""

get_description("create_database.sql")

def get_members(content, member_type):
    members = ""
    if member_type == "procedure":
        start_string = "("
        end_string = ")"
    elif member_type == "package":
        start_string = "("
        end_string = ")"
    elif member_type == "table":
        description = get_description(name)
        create_table_regex = re.compile(r'\bCREATE\sTABLE\s+([^\s\(]+)\s*\((.+?)\);', re.IGNORECASE | re.DOTALL)
        matches = create_table_regex.findall(content)
        
        for table_name, table_content in matches:
            members += f"\n### {table_name.upper()}\n##### Description\n{description[table_name.upper()][0]}\n##### Membres\n"
            columns_regex = re.compile(r'^\s*(\w+)\s+(.+?)(?:,\s*$|\s*$)', re.MULTILINE | re.DOTALL)
            columns = columns_regex.findall(table_content)
            primaryKey = []
            foreignKeys = []

            for column_name, column_type in columns:
                if "primary key" in (column_name + " " + column_type).lower():
                    primaryKey.append(column_name + " " + column_type)
                    if not (column_name.lower().startswith("primary")):
                        members += (f"  - {column_name} ({column_type}) : {description[table_name.upper()][1][(column_name+' ('+column_type+')').strip()]}\n")
                elif "foreign key" in (column_name + " " + column_type).lower():
                    foreignKeys.append(column_name + " " + column_type)
                else:
                    members += (f"  - {column_name} ({column_type}) : {description[table_name.upper()][1][(column_name+' ('+column_type+')').strip()]}\n")
            if len(primaryKey) > 0:
                members += f"##### Primary key\n"
                for primKey in primaryKey:
                    members += (f"  - {primKey}\n")
            if len(foreignKeys) > 0:
                members += "\n##### Foreign Keys\n"
                for forKeys in foreignKeys:
                    members += (f"  - {forKeys}\n")
        return members
    else:
        return members
    
    start_index = content.find(start_string)
    end_index = content.find(end_string, start_index)
    tabMembers = []
    if start_index != -1 and end_index != -1:
        tabMembers=list(map(lambda x: x.strip(), content[start_index+1:end_index].split(",")))
    for member in tabMembers:
        member_name, member_type = member.split(" ")
        members += f"   - {member_name} ({member_type}) : \n"
    return members

try:
    with pysftp.Connection(host, username=username, password=password, cnopts=cnopts) as sftp:
        with sftp.cd('/var/www/equipealt-3/BD/'):
            files = sftp.listdir()
            for name in files:
                if name.endswith(".sql"):
                    with sftp.open(name, 'r') as f:
                        content = f.read().lower()
                        contentString = content.decode("utf-8")
                        if "create procedure" in contentString or "create or replace procedure" in contentString:
                            print(f"{name} : Procédure")
                            members = get_members(contentString, "procedure")
                            procedures.append(f"### {name[0:-4]}\n```sql\n{contentString}\n```\n##### Description\n{get_description(name)}\n##### Membres\n{members}")
                        elif "create trigger" in contentString or "create or replace trigger" in contentString:
                            print(f"{name} : Trigger")
                            triggers.append(f"### {name[0:-4]}\n```sql\n{contentString}\n```\n##### Description\n{get_description(name)}\n")
                        elif "create package" in contentString or "create or replace package" in contentString:
                            print(f"{name} : Package")
                            members = get_members(contentString, "package")
                            packages.append(f"### {name[0:-4]}\n```sql\n{contentString}\n```\n##### Description\n{get_description(name)}\n##### Membres{members}")
                        elif "create table" in contentString or "create or replace table" in contentString:
                            print(f"{name} : Table")
                            members = get_members(contentString, "table")
                            tables.append(f"```sql\n{contentString}\n```\n{members}")
                        else:
                            print(f"{name} : Autre")
    
    rapportGenere = "# Rapport SQL\n"

    if len(tables) > 0:
        rapportGenere += "## Création des tables\n"
        for fichier in tables:
            rapportGenere += fichier + "\n"
    if len(procedures) > 0:
        rapportGenere += "## Création de procédures\n"
        for fichier in procedures:
            rapportGenere += fichier + "\n"
    if len(triggers) > 0:
        rapportGenere += "## Création de triggers\n"
        for fichier in triggers:
            rapportGenere += fichier + "\n"
    if len(packages) > 0:
        rapportGenere += "## Création de packages\n"
        for fichier in packages:
            rapportGenere += fichier + "\n"

    rapportGenere += "\n###### Ce rapport a été généré via un programme disponible ici : https://github.com/Mokocchibi/Utilitaire_compte_rendu_SQL.git"
    
    nom_fichier = "rapportSQL.md"
    
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "w"):
            pass
    
    with open(nom_fichier, "w") as f:
    	f.write(rapportGenere)
    
    #print(rapportGenere)

except pysftp.HostKeysException as e:
    print(f"Error: {e}")
