from io import TextIOWrapper
import json
import numbers
import importlib
import inspect
from ca.uqam.info.mgl7460.meta.jsonclass import JSONClass
from ca.uqam.info.mgl7460.meta.relationship import Relationship

class json_loader:

    # 
    # output_path est le répertoire dans lequel on va générer le
    # code des classes implicites dans le fichier de données
    # json (fourni dans une autre méthode)
    # 
    # Pour faciliter le travail des autres méthodes de cette classes,
    # la classe maintient un dictionnaire "classes", où la clé
    # est le nom de la classe, et la valeur est l'objet JSONClass qui 
    # représente la classe en question
    # 
    # Ici, je me sers du répertoire dans lequel je vais générer le code
    # pour "calculer" le "package cible" des classes générées
    # 
    def __init__(self, output_path: str):
        self.output_path = output_path
        # the package is derived from the output path. It is whatever
        # comes after the first src, from which we replace "/" by "."
        position_of_src = self.output_path.index("/src/")
        self.class_package = self.output_path[position_of_src+5:].replace("/",".")
        print("Package: " + self.class_package)
        self.classes = dict()

    #
    # cette méthode lit un fichier json contenu dans un 
    # fichier portant le nom 'file_name' et se trouvant
    # dans le répertoire input_path
    # 
    # On va se servir du nom du fichier de données comme
    # nom de la classe correspondant à la structure du 
    # fichier json au complet (en enlevant la partie ".json")
    # 
    # Donc, dans notre cas particulier, le nom de la classe
    # recine sera boutique, étant donné que le fichier 
    # source s'appelle boutique.json
    #
    def read_data(self, input_path: str, file_name: str):
        self.input_path = input_path
        self.input_file_name = file_name
        
        # compute root class name based on file name
        self.top_class_name = self.input_file_name.split(".")[0]
        
        # open the file
        json_file = open(self.input_path + '/' + self.input_file_name,'r')
    
        # load the file into a json object
        self.jsobjet = json.load(json_file)


    # 
    # this method creates a JSONClass object with name class_name based 
    # on the structure of the json_fragment passed as an argument
    # If the json_fragment represents an aggregate object, the method
    # will descend recursively creating the component objects, and
    # representing the aggregation links using Relationship objects.
    # 
    # La première fois qu'elle est appelée, on passe comme argument la
    # valeur de self.top_class_name, et de self.jsonobject au complet. Mais
    # cette méthode va s'appeler récursivement avec des noms d'attributs/"relagtions"
    # avec des fragments json de plus en plus petits, correspondant à des objets
    # imbriqués (par exemple boutique --> clients --> commandes --> ligne_commande).
    # 
    # Voir la méthode main(...) de cette classe pour un exemple de "premier appel"
    # de la méthode
    # 
    def build_class(self, class_name: str, json_fragment: dict):
        print ("entering build_class ...\n class_name is: " + class_name + " and json fragment is: " + json_fragment.__str__())

        # Créer un objet JSONClass en passant le nom de la classe cible et
        # du package comme arguments au constructeur. Initialement,
        # la structure de la classe est une "coquille vide".
        # On va ajouter des attributs et des "Relationp"s' en fonction de la
        # structure du fragment json
        current_class = JSONClass(class_name, self.class_package)

        # Maintenant, on itère sur le fragment json, qui est un dictionnaire, dont
        # la partie 'clé' indique un nom d' "attribut" (donnée simple, e.g. nombre ou chaine
        # de caractères), ou un nom de relation, au cas où la valeur correspondante est elle même 
        # une structure complexe
            # 1. si la clé commence par "liste_", on comprend tout de suite que le champ correspondant
            #    correspond à une association (Relationship) liant l'objet présent à une entité dont
            #    le nom se trouve après "liste_""
            #    Par exemple, si la 'clé' du fragment json est "liste_clients", on comprend que
            #    la partie valeur est: a) une liste, et b) que les éléments de la liste sont de type
            #    "client". NOTEZ ici que j'ai enlevé le dernier "s".
            #       
            #    DONC, un champ json portant le nom "liste_produits" (ou "liste_clients") veut dire
            #    que nous avons une association de UN À PLUSIEURS entre <la classe qu'on est en train 
            #    de générer> (ici, 'boutique'), et une entité qui s'appelle "produit" ("client")
            # 
            # 2. si la clé commence par "table_", on comprend que le champ correspondant correspond à
            #    une association (Relationship) UN À PLUSIEURS, qui est INDEXÉE liant l'objet présent 
            #    à une entité dont le nom se trouve après "table_", mais en enlevant le dernier "s".
            #    Dans le fichier boutique.json, il y a UN cas où un champ à une clé commençant par
            #    "table_": il s'agit du 'champ' "table_ligne_commandes", qui fait partie de la représentation
            #    de commande. On en déduit que: on a une entité appelée "ligne_commande" (notez que j'ai 
            #    retiré le dernier "s").
            # 
            #    Que veut dire ici le fait que la relation soit INDEXÉE (i.e. on a "table_" au lieu de 
            #    "liste_"): cela veut dire que: a) la partie à 'valeur' du fragment json est un dictionnaire,
            #    au lieu d'une liste (et donc, au niveau du code généré plus tard, la 'variable d'instance'
            #    correspondente sera un "dict()" plutôt que "[]"). Cela va aussi influencer la façon dont
            #    on va générer le code pour la classe plus tard: dans un cas (relation non indexée), on fait
            #    "append(...)" sur une liste, dans l'autre, on insère une <clé, valeur> avec une expression
            #    du type 'self.table_ligne_commande["TAB1"] = <ligne commande pour le produit avec id "TAB1">
            # 
            #    Quand on insère un objet dans une table (dict()), quel attribut de l'objet doit on utiliser
            #    comme clé? La règle ici est que l'on cherche l'agttribut qui commence par "id_": c'est la
            #    valeur de cet attribut qui va servir comme clé d'insertion.
            #   
            # 3. Si le nom du champ ne commence ni par "liste_" ni par "table_", alors c'est soit: a) un attribut
            #    simple (sa valeur est un type élémentaire de python), b) soit un attribut représentant un objet
            #    complexe, auquel cas on a une association, mais cette fois-ci de UN À UN
            #
            #    Prenons l'exemple d'un fragment de notre fichier de données, qui correspond aux données pour
            #    une cliente: 
            #    { "id": "CL1", "nom": "Tremblay", "prenom": "Sylvie", "adresse": "Saguenay", 
            #    "liste_commandes": [ { "id": "COM1", "table_ligne_commandes": { "CHA1": {"id_produit": "CHA1","quantite": 1},
            #                                                                 "TAB1": {"id_produit": "TAB1","quantite": 1}}},
            #                       { # deuxième commande }]
            #    }
            #     
            #    Parce qu'on a trouvé un champ portant le nom "liste_commandeS", on en déduit que: 1) on a une association
            #    de UN À PLUSIEURS entre 'client' et une entité appelée 'commande' (sans le s), et 2) la valeur du
            #    champ correspondant (ce qui vient après le ":") est une LISTE d'EXEMPLAIRES de 'commande'. On prend
            #    l'un de ces exemplaires (par exemple, le premier de la liste) et on appelle récursivement
            #    build_class(<une variable dont la valeur est 'commande'>, <l'exemplaire JSON en question> )
            #
            #    Rendu dans la construction de 'commande' elle-même, je vais rencontrer "table_ligne_commandeS". On
            #    en débuit que: 1) on a un une association de UN À PLUSIEURS de 'commande' vers une entité appelée
            #    'ligne_commande', 2) la valeur du champ json correspondant n'est PAS une liste de 'ligne_commande',
            #    mais plutôt un dictionnaire avec <clé, valeur> où c'est la partie valeur qui est une 'ligne_commande',
            #    et 3) c'est l'attribut "id_propduit" de 'ligne_commande' qui est utilisé comme clé d'insertion. 
            #    comment je sais ça? en fait, je prends l'attribut (le champ json) de 'ligne_commande' qui a "id_"
            #    comme préfixe (je suppose qu'il y en a un seul)
            #    
        print ('The current class is: \n'+current_class.__str__())

        #insert class in classes dictionary
        self.classes[class_name] = current_class

        # return the constructed class
        return current_class
        

    #
    # the "main" program
    # 
    def main(data_directory:str, input_data_file_name: str, code_output_directory: str):
        # 1. create an instance of loader
        loader = json_loader(code_output_directory)

        # 2. read json data from file
        loader.read_data(data_directory,input_data_file_name)

        # 3. build jsonclass objects 
        top_class = loader.build_class(loader.top_class_name,loader.jsobjet)

        # 4. generate and load python code for python classes corresponding
        # to created jsonclass objets
        for json_class in iter(loader.classes.values()):
            json_class.generate_code(code_output_directory)
            json_class.load_code()

        # 5. read json data and create corresponding python objects
        top_object = top_class.create_object(loader.jsobjet)
        print ("Top object: "+ top_object.__str__())
    
if __name__ == '__main__':

    data_directory = "./data"
    input_data_file_name = "boutique.json"
    code_output_directory = "./src/ca/uqam/info/mgl7460/generated"
    json_loader.main(data_directory, input_data_file_name,code_output_directory)
