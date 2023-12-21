import unittest
from ca.uqam.info.mgl7460.json_loader import json_loader
from ca.uqam.info.mgl7460.meta.relationship import Relationship

class classe_tests_meta (unittest.TestCase):

   # set-up
    def setUp(self):
        self.data_directory = "./data"
        self.input_data_file_name = "boutique.json"
        self.code_output_directory = "./src/ca/uqam/info/mgl7460/generated"
        self.js_loader = json_loader(self.code_output_directory)

    # tester que tous les champs sont proprement initialisés
    def test_lecture_fichier(self):

        # d'abord, vérifier que le fichier existe
        json_file = open(self.data_directory + '/' + self.input_data_file_name,'r')
        self.assertIsNotNone(json_file,"")

        # now load the object
        self.js_loader.read_data(self.data_directory, self.input_data_file_name)

        # now check that js_loader has a non empty json_object
        self.assertIsNotNone(self.js_loader.jsobjet, "The loaded JS object is empty")
        
        # tester que tous les champs sont proprement initialisés

    #
    # cette fonction vérifie que avec le fichier de boutique.json, que les bons
    # objets JSONClass sont créés.
    #
    def test_creation_json_classes(self):

        # load the contents of the input file
        self.js_loader.read_data(self.data_directory, self.input_data_file_name)

        # now check that js_loader has a non empty json_object
        top_class = self.js_loader.build_class('boutique', self.js_loader.jsobjet)

        # first, make sure top_class has name 'boutique'
        self.assertEquals(top_class.name,'boutique', "La classe racine n'est pas Boutique")

        # check that all of the other classes have been created
            # produit
        classe_produit = self.js_loader.classes.get('produit')
        self.assertIsNotNone(classe_produit, "Classe Produit n'a pas été créée")

            # commande
        classe_commande = self.js_loader.classes.get('commande')
        self.assertIsNotNone(classe_commande, "Classe Commande n'a pas été créée")

            # ligne_commande
        classe_ligne_commande = self.js_loader.classes.get('ligne_commande')
        self.assertIsNotNone(classe_ligne_commande, "Classe Commande n'a pas été créée")

            # client
        classe_client = self.js_loader.classes.get('client')
        self.assertIsNotNone(classe_client, "Classe Client n'a pas été créée")

        # check the contents of client
            # attributes
        self.assertIn('id',classe_client.attributes.keys(),"class Client does not have attribute 'id'")
        self.assertIn('nom',classe_client.attributes.keys(),"class Client does not have attribute 'nom'")
        self.assertIn('prenom',classe_client.attributes.keys(),"class Client does not have attribute 'prenom'")
        self.assertIn('adresse',classe_client.attributes.keys(),"class Client does not have attribute 'adresse'")

    #
    # cette fonction vérifie que avec le fichier de boutique.json, que les bons
    # objets Relationship sont créés.
    #
    def test_creation_relationships(self):

        # load the contents of the input file
        self.js_loader.read_data(self.data_directory, self.input_data_file_name)

        # now build the classes
        self.js_loader.build_class('boutique', self.js_loader.jsobjet)

        # get the main class objects
            # commande
        classe_commande = self.js_loader.classes.get('commande')

            # client
        classe_client = self.js_loader.classes.get('client')

            # relationships
        client_commande_relationship = classe_client.relationships['liste_commandes']

        # d'abord, vérifie que la relation existe
        self.assertIsNotNone(client_commande_relationship,"Pas de relation dans Client avec le nom 'liste_commandes'")

        # vérifie ses propriétés
        self.assertEquals(client_commande_relationship.source_entity,'client',"Client n'est pas l'entité source de " + client_commande_relationship.__str__())
        self.assertEquals(client_commande_relationship.destination_entity,'commande',"Client n'est pas l'entité destination de " + client_commande_relationship.__str__())
        self.assertEquals(client_commande_relationship.multiplicity,Relationship.ONE_TO_MANY, "Multiplicité de " + client_commande_relationship.__str__() + " n'est pas ONE-TO-MANY")
        self.assertFalse(client_commande_relationship.is_indexed(), client_commande_relationship.__str__() + " est indexée alors qu'elle n'est pas supposée")

        # Relation entre commande et lignes produit
        commande_produit_relationship = classe_commande.relationships['table_ligne_commandes']

        # d'abord, vérifie que la relation existe
        self.assertIsNotNone(commande_produit_relationship,"Pas de relation dans Client avec le nom 'liste_commandes'")

        # ensuite vérifie ses autres propriétés
        self.assertEquals(commande_produit_relationship.source_entity,'commande',"commande n'est pas l'entité source de " + commande_produit_relationship.__str__())
        self.assertEquals(commande_produit_relationship.destination_entity,'ligne_commande',"ligne_commande n'est pas l'entité destination de " + commande_produit_relationship.__str__())
        self.assertEquals(commande_produit_relationship.multiplicity,Relationship.ONE_TO_MANY, "Multiplicité de " + commande_produit_relationship.__str__() + " n'est pas ONE-TO-MANY")
        self.assertEquals(commande_produit_relationship.index_field,'id_produit',"L'index pour les lignes commandes n'est pas 'id_produit'")
        self.assertTrue(commande_produit_relationship.is_indexed(), commande_produit_relationship.__str__() + " n'est indexée alors qu'elle est supposée l'être")


    #
    # cette fonction vérifie que avec le fichier de boutique.json, que les bons
    # modules python ont été générés, et qu'ils compilent
    #
    def test_generation_chargement_code(self):

        # 1. load the contents of the input file
        self.js_loader.read_data(self.data_directory, self.input_data_file_name)

        # 2. now build the classes
        self.js_loader.build_class('boutique', self.js_loader.jsobjet)

        # 3. generate and load python code for python classes corresponding
        # to created jsonclass objets
        for js_class in iter(self.js_loader.classes.values()):
            # 3.1 générer le code
            js_class.generate_code(self.code_output_directory)

            # 3.2 on vérifie que le fichier a bel et bien été généré
            json_file = open(js_class.generated_class_file_name,'r')
            self.assertIsNotNone(json_file,"Il n'y a pas de fichier portant le nom " + js_class.generated_class_file_name)

            # 3.3 on charge le code
            js_class.load_code()

            # 3.4 on vérifie que le code a bel et bien été compilé en 
            # vérifant l'attribut 'type' de json_class
            objet_type = js_class.type
            self.assertIsNotNone(objet_type, "Une version compilée du code n'a pas été générée ou affectée")

            # 3.5 vérifier que l'objet type en question porte le bon nom
            self.assertEquals(js_class.package+"."+js_class.name,objet_type.__module__, "Les noms ne matchent pas")


    #
    # cette fonction vérifie que avec le fichier de boutique.json, que les bons
    # modules python ont été générés, et qu'ils compilent
    #
    def test_creation_et_chargement_objets(self):

        # 1. load the contents of the input file
        self.js_loader.read_data(self.data_directory, self.input_data_file_name)

        # 2. now build the classes
        top_class = self.js_loader.build_class('boutique', self.js_loader.jsobjet)

        # 3. generate and load python code for python classes corresponding
        # to created jsonclass objets
        for js_class in iter(self.js_loader.classes.values()):
            # 3.1 générer le code
            js_class.generate_code(self.code_output_directory)

            # 3.2 on charge le code
            js_class.load_code()

        # 4. read json data and create corresponding python objects
        top_object = top_class.create_object(self.js_loader.jsobjet)

        # 5. on teste le contenu de 'top_object'

        # 5.1, d'abord, qu'il est du bon type
        self.assertIsInstance(top_object,top_class.type, "L'objet crée n'est pas du bon type")

        # 5.2 ensuite que la valeur de son attribut 'nom' est 'MGL7460 Bazaar'
        self.assertEquals(top_object.nom,"MGL7460 Bazaar", "L'objet " + top_object.__str__() + " n'a pas le bon nom")

        # 5.3 ensuite qu'il a une liste de produit contenant 3 produits
        self.assertEquals(len(top_object.liste_produits),3, "L'objet " + top_object.__str__()+" n'a pas trois produits")

        # 5.4 ensuite qu'il a une liste de client contenant 2 clients
        self.assertEquals(len(top_object.liste_clients),2, "L'objet " + top_object.__str__()+" n'a pas deux clients")

        # 5.5 ensuite que Sylvie Tremblay a passé deux commandes
            # 5.5.1 trouver les commandes de sylvie
        for cl in top_object.liste_clients:
            if (cl.nom == "Tremblay"):
                commandes_sylvie = cl.liste_commandes
            # 5.5.2 leur nombre est egal à 2
        self.assertEquals(len(commandes_sylvie),2)

            # 5.5.3 commande 1 includes one table
        commande_1 = [commande for commande in commandes_sylvie if commande.id == 'COM1'][0]
        self.assertEquals(commande_1.id, 'COM1',"commande_1 n'a pas le bon identificateur")

        quantite_tables = commande_1.table_ligne_commandes['TAB1'].quantite
        self.assertEquals(quantite_tables,1,"Nombre de TAB1 commandés est faux")


    # tear down
    def tearDown(self):
        print('Bye, bye!')


if __name__ == '__main__':

    unittest.main()
