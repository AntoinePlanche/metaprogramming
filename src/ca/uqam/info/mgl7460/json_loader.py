import json
from ca.uqam.info.mgl7460.meta.jsonclass import JSONClass
from ca.uqam.info.mgl7460.meta.relationship import Relationship

class json_loader:

    # Output_path est le répertoire dans lequel on va générer le
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
    def __init__(self, output_path: str):
        self.output_path = output_path
        # the package is derived from the output path. It is whatever
        # comes after the first src, from which we replace "/" by "."
        position_of_src = self.output_path.index("/src/")
        self.class_package = self.output_path[position_of_src+5:].replace("/",".")
        print("Package: " + self.class_package)
        self.classes = dict()


    # Cette méthode lit un fichier json contenu dans un 
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
    def read_data(self, input_path: str, file_name: str):
        self.input_path = input_path
        self.input_file_name = file_name
        
        # Compute root class name based on file name
        self.top_class_name = self.input_file_name.split(".")[0]
        
        # Open the file
        json_file = open(self.input_path + '/' + self.input_file_name,'r')
    
        # Load the file into a json object
        self.jsobjet = json.load(json_file)


    # This method creates a JSONClass object with name class_name based 
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
    def build_class(self, class_name: str, json_fragment: dict):
        print ("entering build_class ...\n class_name is: " + class_name + " and json fragment is: " + json_fragment.__str__())

        # Crée un objet JSONClass pour la classe actuelle
        current_class = JSONClass(class_name, self.class_package)

        # Itére sur le fragment json
        for key, value in json_fragment.items():
            if isinstance(value, list):
                self.proccess_list(current_class, key, value)
            elif isinstance(value, dict):
                self.proccess_dict(current_class,key,value)
            else:
                # Attribut simple
                current_class.add_attribute(key, type(value).__name__)

        print ('The current class is: \n'+current_class.__str__())

        #insert class in classes dictionary
        self.classes[class_name] = current_class

        # return the constructed class
        return current_class
    
    # To reduce the complexity of the build_class method this method was created
    # it procces the value being a list
    def proccess_list(self, current_class, key, list:list):
        # Traitement d'une liste : relation ONE_TO_MANY non indexée
        related_class_name = key[6:] if key.startswith("liste_") else key
        if related_class_name.endswith('s'):
            related_class_name = related_class_name[:-1]  # Enleve le 's' final
        relation_name = related_class_name # Nom de la relation
        current_class.add_relationship(relation_name, related_class_name, Relationship.ONE_TO_MANY)

        # Appel récursif pour chaque élément de la liste
        for item in list:
            self.build_class(related_class_name, item)

    # To reduce the complexity of the build_class method this method was created
    # it procces the value being a dictionnary
    def proccess_dict(self, current_class, key, dict:dict):
        if key.startswith("table_"):
            # Traitement d'un dictionnaire : relation ONE_TO_MANY indexée ou attribut complexe
            related_class_name = key[6:]
            if related_class_name.endswith('s'):
                related_class_name = related_class_name[:-1]
            relation_name = related_class_name  # Nom de la relation
            # Identifie le champ d'indexation en parcourant les clés de l'objet
            sample_item = next(iter(dict.values()))
            index_field = next((k for k in sample_item.keys() if k.startswith('id')), 'id_' + related_class_name)
            current_class.add_relationship(relation_name, related_class_name, Relationship.ONE_TO_MANY, index_field)

            # Appel récursif pour chaque valeur du dictionnaire
            for item in dict.values():
                self.build_class(related_class_name, item)
        else:
            # Relation ONE_TO_ONE ou attribut complexe
            related_class_name = key  # Le nom de la classe liée est la clé elle-même
            relation_name = related_class_name  # Nom de la relation
            current_class.add_relationship(relation_name, related_class_name, Relationship.ONE_TO_ONE)
            self.build_class(related_class_name, dict) # Appel récursif pour l'objet complexe
        

    # The "main" program
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
        print ("\n\nTop object: "+ top_object.__str__())


if __name__ == '__main__':

    data_directory = "./data"
    input_data_file_name = "boutique.json"
    code_output_directory = "./src/ca/uqam/info/mgl7460/generated"
    json_loader.main(data_directory, input_data_file_name,code_output_directory)
