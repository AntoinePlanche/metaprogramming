from io import TextIOWrapper
import importlib
import json

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
        constructor_header += ", ".join(f"{name}: {type_.__name__}" for name, type_ in self.attributes.items())
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
                    python_file.write(f"        self.{relation.name} = {{}}\n")
                # 3.2.2 It is not indexed
                else:
                    python_file.write(f"        self.{relation.name} = []\n")

        python_file.write("\n\n")    


    # This method generates the __str__ method. it simply prints
    # the attributes and relationships of the object. It will
    # descend recursively if each object in the object tree
    # has a customer __str__() methods that prints its
    # fields      
    def generate__str__method(self, python_file: TextIOWrapper):
        # 1. Génére l'en-tête de la fonction
        python_file.write("    def __str__(self):\n")
        python_file.write("        str_repr = ''\n")

        # 2. Génére les instructions qui imprimeront les attributs
        for attr_name in self.attributes:
            python_file.write(f"        str_repr += '{attr_name}: {{{attr_name}}}, ' if self.{attr_name} is not None else ''\n")
        
        # 3. Génére les instructions qui imprimeront les relations
        for relation in iter(self.relationships.values()):
            if relation.index_field:
                # Pour les relations indexées (comme les dictionnaires)
                python_file.write(f"        str_repr += '    {relation.name}: ' + str({{key: value for key, value in self.{relation.name}.items()}}) + '\\n'\n")
            else:
                # Pour les relations non indexées (comme les listes)
                python_file.write(f"        str_repr += '    {relation.name}: ' + str(list(self.{relation.name})) + '\\n'\n")
                pass

        # 4. Ajoute le retour de la fonction et le retour chariot
        python_file.write("        return str_repr[:-2] if str_repr else 'Empty JSONClass Object'\n")
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
        adder_code = f"    def add_{relation_name}(self, item):\n"

        if relation.index_field is None:
            # Cas pour une liste : ajouter l'élément à la liste
            adder_code += f"        self.{relation_name}.append(item)\n"
        else:
            # Cas pour un dictionnaire : ajouter l'élément avec l'index_field comme clé
            adder_code += f"        self.{relation_name}[item.{relation.index_field}] = item\n"

        return adder_code + "\n"


    # depending on whether we have a list or table, we will either 
    # use "self.<relation name>.remove(parameter_name)" 
    # or "self.<relation name>.pop(parameter_name.<index field>)"
    # where <index field> is relation.index_field. Thus, the expression
    # is "self.<relation name>.pop(parameter_name.<relation.index_field>)"
    def get_remover_string(self, relation_name: str, relation: Relationship)-> str:
        # En-tête de la méthode remover
        remover_code = f"    def remove_{relation_name}(self, item):\n"

        if relation.index_field is None:
            # Cas pour une liste : supprimer l'élément de la liste
            remover_code += f"        if item in self.{relation_name}:\n"
            remover_code += f"            self.{relation_name}.remove(item)\n"
        else:
            # Cas pour un dictionnaire : supprimer l'élément en utilisant l'index_field comme clé
            remover_code += f"        key = item.{relation.index_field}\n"
            remover_code += f"        if key in self.{relation_name}:\n"
            remover_code += f"            self.{relation_name}.pop(key)\n"

        return remover_code + "\n"


    # depending on whether we have a list or table, we will either 
    # use "iter(self.<relation name>)" or 
    # or "iter(self.<relation name>.values())"
    def get_iterator_string(self, relation_name: str, relation: Relationship)-> str:
        # En-tête de la méthode iterator
        iterator_code = f"    def iterate_{relation_name}(self):\n"

        if relation.index_field is None:
            # Cas pour une liste : renvoyer un itérateur sur la liste
            iterator_code += f"        return iter(self.{relation_name})\n"
        else:
            # Cas pour un dictionnaire : renvoyer un itérateur sur les valeurs du dictionnaire
            iterator_code += f"        return iter(self.{relation_name}.values())\n"

        return iterator_code + "\n"


    # An indexed accessor function, which takes a key as a parameter
    def get_indexed_accessor_string(self, relation_name: str, relation: Relationship)-> str:
        # On s'assure que la relation est effectivement indexée
        if relation.index_field is None:
            return ""

        # En-tête de la fonction d'accès indexée
        indexed_accessor_code = f"    def get_{relation_name}(self, key):\n"

        # Générer le code pour accéder à un élément en utilisant la clé
        indexed_accessor_code += f"        return self.{relation_name}.get(key, None)\n"

        return indexed_accessor_code + "\n"


    # This function takes as an argument a class name and a json
    # object/fragment, and creates an object of the corresponding 
    # class and populates its fields with the contents of json_fragment
    # 
    # Depending on the structure of the class, if the class has relationships
    # to other classes, then objects of the other classes are created, 
    # recursively.
    # 
    def create_object(self, json_fragment: str):
        # Convertir le fragment JSON en un dictionnaire Python
        data = json.loads(json_fragment)

        # 1. Construire l'objet
        # 1.1. Obtenir la liste des paramètres du constructeur
        constructor_params = {attr: data.get(attr, None) for attr in self.attributes}

        # 1.2. Créer une chaîne représentant l'invocation du constructeur
        constructor_invocation = f"{self.name}(**{constructor_params})"

        # 1.3. Évaluer l'expression pour créer l'objet
        # C'est risqué et inutilisable comme cela en production mais j'ai confiance dans Pr. Mili
        new_object = eval(constructor_invocation)

        # 2. Ajouter maintenant les relations
        for relation in iter(self.relationships.values()):
            relation_value = data.get(relation.name, [])

            if (relation.is_indexed()):
                # 2.1.a Gérer comme une table (dictionnaire)
                for value in relation_value.values():
                    # Créer l'objet de destination et l'ajouter à la relation
                    related_object = JSONClass.JSON_CLASSES[relation.target_type_name].create_object(json.dumps(value))
                    getattr(new_object, f"add_{relation.name}")(related_object)
            else:
                # 2.1.b Gérer comme une simple liste
                for item in relation_value:
                    # Créer l'objet de destination et l'ajouter à la relation
                    related_object = JSONClass.JSON_CLASSES[relation.target_type_name].create_object(json.dumps(item))
                    getattr(new_object, f"add_{relation.name}")(related_object)
                    
        return new_object
