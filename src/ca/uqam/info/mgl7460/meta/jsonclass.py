from io import TextIOWrapper
import importlib
import inspect

from ca.uqam.info.mgl7460.meta.relationship import Relationship


class JSONClass:

    # a dictionary of JSON classes, indexed by fully qualified class name
    JSON_CLASSES = dict()

    # creates an instance of a JSONClass, and adds it to the JSON_CLASSES global
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


    # this method 
    def set_attribute_value(self, receiver: object, attribute_name: str, attribute_value: object):
        pass


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

    # 
    # This method loads the code for this (self) JSONClass object,
    # and returns the corresponding type.
    # 
    def load_code(self):
        # 1. First check whether the code was generated. 
        # if not, it returns None

        if (self.generated_class_file_name == None):
            return None
        
        # 2. now, load the corresponding module
        module = importlib.import_module(self.fully_qualified_name())
        print("The module is: " + module.__str__())

        # 3. get the 'type' object that represents the 'compiled version'
        #    of this JSONClass. I called it class_class_object in my code
        #    
        #    Quand vous aurez fait cela, enlevez le commentaire
        # 
        # self.type = class_class_object
        return self.type

    # By default, the constructor will take a value for each attribute, and initialize it.
    # It will also initialize ONE_TO_MANY relationships to en empty collection
    # of whichever structure is appropriate: a) a list, or b) a map (if the relationship
    # is indexed)
    def generate_constructor(self, python_file: TextIOWrapper):
        # 1. Generate header

        # 2. Generate code to initialize attributes
        
        # 3. Generate code to initialize relationships
            # 3.1 if ONE_TO_ONE, initialize to None

            # 3.2 if ONE_TO_MANY, check if the relation is indexed or not
                # 3.2.1 It is indexed

        python_file.write("\n\n")    

    #
    # This method generates the __str__ method. it simply prints
    # the attributes and relationships of the object. It will
    # descend recursively if each object in the object tree
    # has a customer __str__() methods that prints its
    # fields
    #         
    def generate__str__method(self, python_file: TextIOWrapper):
        # 1. generate the function header

        # 2. second, generate the statements that will print the attributes
        
        # 3. third, generate the statements that will print 
        # the relations.
        for relation in iter(self.relationships.values()):
            # depending on whether the relation is indexed or not, different code
            # should be generated
            pass
        

        # 4. add __str__ code to the file
        # python_file.write(__str__code)
        python_file.write("\n") 



    #
    # This method generates accessors for collection-like attributes, i.e. ONE_TO_MANY
    # (indexed or not) relationships. For those, we need to provide methods to add,
    # remove, and iterate
    #         
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
        adder_code = ""
        return adder_code

    # depending on whether we have a list or table, we will either 
    # use "self.<relation name>.remove(parameter_name)" 
    # or "self.<relation name>.pop(parameter_name.<index field>)"
    # where <index field> is relation.index_field. Thus, the expression
    # is "self.<relation name>.pop(parameter_name.<relation.index_field>)"
    def get_remover_string(self, relation_name: str, relation: Relationship)-> str:
        remover_code = ""
        return remover_code

    # depending on whether we have a list or table, we will either 
    # use "iter(self.<relation name>)" or 
    # or "iter(self.<relation name>.values())"
    def get_iterator_string(self, relation_name: str, relation: Relationship)-> str:
        iterator_code = ""
        return iterator_code

    # an indexed accessor function, which takes a key as a parameter
    def get_indexed_accessor_string(self, relation_name: str, relation: Relationship)-> str:
        indexed_accessor_code = ""

        return indexed_accessor_code


    # 
    # This function takes as an argument a class name and a json
    # object/fragment, and creates an object of the corresponding 
    # class and populates its fields with the contents of json_fragment
    # 
    # Depending on the structure of the class, if the class has relationships
    # to other classes, then objects of the other classes are created, 
    # recursively.
    # 
    def create_object(self, json_fragment: str):
        # 1. construct object
        # 1.1. get list of constructor parameters
        
        # 1.2. create a string that represents the invocation of the constructor

        # 1.3. evaluate the expression to create the object

        # 2. Now, add the relationships. Utiliser l'information
        #    contenue dans self.relationships pour savoir
        #    comment 'interpreter' le fragment json, et quelle
        #    méthode invoquer pour lier les objets créés
        for relation in iter(self.relationships.values()):
            # 2.1 check if it is a list or table to determine 
            # how to handle relation_value
            if (relation.is_indexed()):
                # 2.1.a it is table, and thus, a list of 
                # key value pairs. In this case, iterate 
                # over the keys of relation_value, and: i) create an
                # an object with the value part, and ii) insert it in the
                # new_objet with the appropriate insert method that uses
                # the key part as an index

                    # 2.1.a.1 get the JSONClass representing the destination entity

                    # 2.1.a.2 get the json fragment corresponding to the destination entity

                    # 2.1.a.3 recursively, create the destination entity using the corresponding
                    # json class objet

                    # 2.1.a.4 now, add the component object to the current object using its corresponding
                    # indexed accessor
                pass

            else:
                # 2.1.b It is a simple list. Thus relation_value is a list of
                # json fragments representing individual objects
                
                    # 2.1.b.1 get the JSONClass representing the destination entity
                
                    # 2.1.b.2 recursively, create the destination entity using the corresponding
                    # json class objet
                
                    # 2.1.a.4 now, add the component object to the current object using its corresponding
                    # indexed accessor
                pass
                    


        # return new_object