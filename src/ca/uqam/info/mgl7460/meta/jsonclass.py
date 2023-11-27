from io import TextIOWrapper
import importlib

from ca.uqam.info.mgl7460.meta.relationship import Relationship


class JSONClass:

    # A dictionary of JSON classes, indexed by fully qualified class name
    JSON_CLASSES = dict()

    # Creates an instance of a JSONClass, and adds it to the JSON_CLASSES global
    # dictionary, indexed by fully qualified name
    def __init__(self, name: str, package: str):
        self.name = name
        self.package = package
        self.attributes = dict()
        self.relationships = dict()
        self.type = None
        self.generated_class_file_name= None
        JSONClass.JSON_CLASSES[self.name] = self


    def fully_qualified_name(self):
        return self.package + "." + self.name


    def add_attribute(self, attributeName: str, valueType=object)-> None:
        self.attributes[attributeName]=valueType


    # This method 
    def set_attribute_value(self, receiver: object, attribute_name: str, attribute_value: object):
         # Vérifie si l'attribut existe dans la classe de l'objet 'receiver'
        if attribute_name in self.attributes:
            # Définis la valeur de l'attribut
            setattr(receiver, attribute_name, attribute_value)
        else:
            # On leve une exception si l'attribut n'existe pas dans la classe de l'objet 'receiver'
            raise AttributeError(f"L'attribut '{attribute_name}' n'existe pas dans la classe '{receiver.__class__.__name__}'.")


    # Adds a relationship from the current class to an entity named target_type_name
    def add_relationship(self, relation_name: str, target_type_name: str, multiplicity: int, index_field: str = None):
        relationship = Relationship(relation_name,self.name, target_type_name, multiplicity, index_field)
        self.add_relationship_object(relationship)


    def add_relationship_object(self, relationship):
        self.relationships[relationship.name] =relationship


    def __str__(self) -> str:
        display_string = self.name +"\n"
        display_string = display_string + "\tAttributs:\n"
        for att_name in iter(self.attributes):
            display_string = display_string + "\t\t" + att_name + " :" + self.attributes.get(att_name)+ "\n"
        
        display_string = display_string + "\tRelations:\n"
        for relation_name in iter(self.relationships):
            display_string = display_string + "\t\t" + self.relationships.get(relation_name).__str__() + "\n"
        return display_string


    # This method generates the code for this (self) JSONClass object.
    # 
    # If the class refers to user classes, and those have not been generated
    # yet, they are recursively generated and imported
    def generate_code(self, output_path: str):
        file_name = output_path + "/" + self.name + ".py"
        # 1. open the file
        python_file = open(file_name,'w+')

        # 2. print class header
        python_file.write("class " + self.name + ":\n")

        # 3. generate constructor
        self.generate_constructor(python_file)

        # 4. generate accessors
        self.generate_accessors(python_file)

        # 5. generate __str__ method
        self.generate__str__method(python_file)

        # 6. close the file
        python_file.close()

        # 7. mark the class as having been generated, by
        # specifying the name of the code file
        self.generated_class_file_name= file_name


    # This method loads the code for this (self) JSONClass object,
    # and returns the corresponding type.
    def load_code(self):
        # 1. First check whether the code was generated. 
        # if not, it returns None

        if (self.generated_class_file_name == None):
            return None
        
        # 2. now, load the corresponding module
        module = importlib.import_module(self.fully_qualified_name())
        print("The module is: " + module.__str__())

        # 3. Obtenir le type de l'objet qui représente la version 'compilée' de cette JSONClass
        # Le nom de la classe est supposé être le même que self.name
        class_class_object = getattr(module, self.name)

        # Stocker ce type dans self.type pour une utilisation future
        self.type = class_class_object

        # self.type = class_class_object
        return self.type


    # By default, the constructor will take a value for each attribute, and initialize it.
    # It will also initialize ONE_TO_MANY relationships to en empty collection
    # of whichever structure is appropriate: a) a list, or b) a map (if the relationship
    # is indexed)
    def generate_constructor(self, python_file: TextIOWrapper):
        # 1. Generate header
        constructor_header = "    def __init__(self, "
        constructor_header += ", ".join(f"{name}: {type_}" for name, type_ in self.attributes.items())
        constructor_header += "):\n"
        python_file.write(constructor_header)
        # 2. Generate code to initialize attributes
        for name in self.attributes:
            python_file.write(f"        self.{name} = {name}\n")
        # 3. Generate code to initialize relationships
        for relation in self.relationships.values():
            # 3.1 if ONE_TO_ONE, initialize to None
            if relation.multiplicity == Relationship.ONE_TO_ONE:
                python_file.write(f"        self.{relation.name} = None\n")
            # 3.2 if ONE_TO_MANY, check if the relation is indexed or not
            elif relation.multiplicity == Relationship.ONE_TO_MANY:
                # 3.2.1 It is indexed
                if relation.index_field:
                    python_file.write(f"        self.table_{relation.name}s = {{}}\n")
                # 3.2.2 It is not indexed
                else:
                    python_file.write(f"        self.liste_{relation.name}s = []\n")

        python_file.write("\n")    


    # This method generates the __str__ method. it simply prints
    # the attributes and relationships of the object. It will
    # descend recursively if each object in the object tree
    # has a customer __str__() methods that prints its
    # fields      
    def generate__str__method(self, python_file: TextIOWrapper):
        # 1. Génére l'en-tête de la fonction
        python_file.write(f"    def __str__(self) -> str:\n")
        python_file.write(f"        return_string = \"{self.name}[\"\n")

        # 2. Génére les instructions qui imprimeront les attributs
        for attr_name in self.attributes:
            python_file.write(f"        return_string += \"{attr_name} = \" + self.{attr_name}.__str__() + \", \" \n")
        
        # 3. Génére les instructions qui imprimeront les relations
        for relation in iter(self.relationships.values()):
            if relation.index_field:
                # Pour les relations indexées (comme les dictionnaires)
                python_file.write(f"        relation_str_ = \"table_{relation.name}s\" + \" = [\"\n")
                python_file.write(f"        for key in iter(self.table_{relation.name}s.keys()):\n")
                python_file.write(f"            relation_str_ += key + \" -> \" + self.table_{relation.name}s[key].__str__() + \", \"\n")
                python_file.write("        relation_str_ = relation_str_[:-2] + \"]\"\n")
                python_file.write("        return_string += relation_str_ + \", \"\n")
            else:
                # Pour les relations non indexées (comme les listes)
                python_file.write(f"        relation_str_ = \"liste_{relation.name}s\" + \" = [\"\n")
                python_file.write(f"        for related in iter(self.liste_{relation.name}s):\n")
                python_file.write(f"            relation_str_ += related.__str__() + \", \"\n")
                python_file.write("        relation_str_ = relation_str_[:-2] + \"]\"\n")
                python_file.write("        return_string += relation_str_ + \", \"\n")

        # 4. Ajoute le retour de la fonction et le retour chariot
        python_file.write("        return_string = return_string[:-2] + \"]\"\n")
        python_file.write("        return return_string")
        python_file.write("\n")


    # This method generates accessors for collection-like attributes, i.e. ONE_TO_MANY
    # (indexed or not) relationships. For those, we need to provide methods to add,
    # remove, and iterate   
    def generate_accessors(self, python_file: TextIOWrapper):
        # Iterate over the relationships
        for relation_name in iter(self.relationships.keys()):
            relation = self.relationships[relation_name]

            # 1. generate adder
            adder_string = self.get_adder_string(relation_name,relation)
            python_file.write(adder_string)

            # 2. generate remover
            remover_string = self.get_remover_string(relation_name,relation)
            python_file.write(remover_string)

            # 3. generate iterator
            iterator_string = self.get_iterator_string(relation_name,relation)
            python_file.write(iterator_string)

            # 4. generate indexed accerssor, if relation is indexed
            if (relation.index_field != None):
                indexed_accessor_string = self.get_indexed_accessor_string(relation_name,relation)
                python_file.write(indexed_accessor_string)
     

    # depending on whether we have a list or table, we will either 
    # use "self.<relation name>.append(parameter_name)" 
    # or "self.<relation name>[parameter.<index field>] = parameter "
    # where <index field> is relation.index_field. Thus, the expression
    # is "self.<relation name>[parameter_name.<relation.index_field>] = parameter_name "
    def get_adder_string(self, relation_name: str, relation: Relationship)-> str:
        # En-tête de la méthode adder
        adder_code = f"    def add_{relation_name}(self, a_{relation_name}):\n"
        if relation.index_field is None:
            # Cas pour une liste : ajouter l'élément à la liste
            adder_code += f"        self.liste_{relation_name}s.append(a_{relation_name})\n"
        else:
            # Cas pour un dictionnaire : ajouter l'élément avec l'index_field comme clé
            adder_code += f"        self.table_{relation_name}s[a_{relation_name}.{relation.index_field}] = a_{relation_name}\n"

        return adder_code + "\n"


    # depending on whether we have a list or table, we will either 
    # use "self.<relation name>.remove(parameter_name)" 
    # or "self.<relation name>.pop(parameter_name.<index field>)"
    # where <index field> is relation.index_field. Thus, the expression
    # is "self.<relation name>.pop(parameter_name.<relation.index_field>)"
    def get_remover_string(self, relation_name: str, relation: Relationship)-> str:
        if relation.index_field is None:
            # En-tête de la méthode remover
            remover_code = f"    def remove_{relation_name}(self, a_{relation_name}):\n"
            # Cas pour une liste : supprimer l'élément de la liste
            remover_code += f"        if a_{relation_name} in self.liste_{relation_name}s:\n"
            remover_code += f"            self.liste_{relation_name}s.remove(a_{relation_name})\n"
        else:
            # En-tête de la méthode remover
            remover_code = f"    def remove_{relation_name}_with_{relation.index_field}(self, {relation.index_field}):\n"
            # Cas pour un dictionnaire : supprimer l'élément en utilisant l'index_field comme clé
            remover_code += f"        if {relation.index_field} in self.table_{relation_name}s:\n"
            remover_code += f"            self.table_{relation_name}s.pop({relation.index_field})\n"
        return remover_code + "\n"


    # depending on whether we have a list or table, we will either 
    # use "iter(self.<relation name>)" or 
    # or "iter(self.<relation name>.values())"
    def get_iterator_string(self, relation_name: str, relation: Relationship)-> str:
        if relation.index_field is None:
            # En-tête de la méthode iterator
            iterator_code = f"    def get_liste_{relation_name}s(self):\n"
            # Cas pour une liste : renvoyer un itérateur sur la liste
            iterator_code += f"        return iter(self.liste_{relation_name}s)\n"
        else:
            # En-tête de la méthode iterator
            iterator_code = f"    def get_table_{relation_name}s(self):\n"
            # Cas pour un dictionnaire : renvoyer un itérateur sur les valeurs du dictionnaire
            iterator_code += f"        return iter(self.table_{relation_name}s.values())\n"

        return iterator_code + "\n"


    # An indexed accessor function, which takes a key as a parameter
    def get_indexed_accessor_string(self, relation_name: str, relation: Relationship)-> str:
        # On s'assure que la relation est effectivement indexée
        if relation.index_field is None:
            return ""
        # Trouve la classe cible dans le dictionnaire global des classes JSON
        target_class = JSONClass.JSON_CLASSES.get(relation.destination_entity)
        if target_class is None:
            raise ValueError(f"Classe cible '{relation.destination_entity}' non trouvée.")
        
        # Trouver le type de l'index_field dans les attributs de la classe cible
        index_field_type = target_class.attributes.get(relation.index_field, object)
        
        # En-tête de la fonction d'accès indexée
        indexed_accessor_code = f"    def get_{relation_name}_with_{relation.index_field}(self, {relation.index_field} : {index_field_type}):\n"

        # Générer le code pour accéder à un élément en utilisant la clé
        indexed_accessor_code += f"        return self.table_{relation_name}s.get({relation.index_field}, None)\n"

        return indexed_accessor_code + "\n"


    # This function takes as an argument a class name and a json
    # object/fragment, and creates an object of the corresponding 
    # class and populates its fields with the contents of json_fragment
    # 
    # Depending on the structure of the class, if the class has relationships
    # to other classes, then objects of the other classes are created, 
    # recursively.
    def create_object(self, json_fragment: dict):
        # Charger le module contenant la classe
        module = importlib.import_module(self.package + '.' + self.name)
        if not hasattr(module, self.name):
            raise ImportError(f"Classe {self.name} non trouvée dans le module {self.package}")
        
        # Obtenir une référence à la classe
        class_ref = getattr(module, self.name)
        # Vérifie si class_ref est bien une classe
        if not isinstance(class_ref, type):
            raise TypeError(f"{self.name} dans {self.package} n'est pas une classe")
        
        # 1. Construire l'objet avec les paramètres du constructeur
        constructor_params = {attr: json_fragment.get(attr, None) for attr in self.attributes}
        new_object = class_ref(**constructor_params)

        # 2. Ajouter maintenant les relations
        for relation in iter(self.relationships.values()):
            if (relation.is_indexed()):
                relation_value = json_fragment.get(f"table_{relation.name}s", [])
                # 2.1.a Gérer comme une table (dictionnaire)
                for value in relation_value.values():
                    # Créer l'objet de destination et l'ajouter à la relation
                    related_object = JSONClass.JSON_CLASSES[relation.destination_entity].create_object(value)
                    getattr(new_object, f"add_{relation.name}")(related_object)
            else:
                relation_value = json_fragment.get(f"liste_{relation.name}s", [])
                # 2.1.b Gérer comme une simple liste
                for item in relation_value:
                    # Créer l'objet de destination et l'ajouter à la relation
                    related_object = JSONClass.JSON_CLASSES[relation.destination_entity].create_object(item)
                    getattr(new_object, f"add_{relation.name}")(related_object)
                    
        return new_object