class boutique:
    def __init__(self, nom: str):
        self.nom = nom
        self.liste_produits = []
        self.liste_clients = []

    def add_produit(self, a_produit):
        self.liste_produits.append(a_produit)

    def remove_produit(self, a_produit):
        if item in self.liste_produits:
            self.liste_produits.remove(a_produit)

    def get_liste_produits(self):
        return iter(self.liste_produits)

    def add_client(self, a_client):
        self.liste_clients.append(a_client)

    def remove_client(self, a_client):
        if item in self.liste_clients:
            self.liste_clients.remove(a_client)

    def get_liste_clients(self):
        return iter(self.liste_clients)

    def __str__(self):
        str_repr = ''
        str_repr += 'nom: {nom}, ' if self.nom is not None else ''
        str_repr += '    produit: ' + str(list(self.produit)) + '\n'
        str_repr += '    client: ' + str(list(self.client)) + '\n'
        return str_repr[:-2] if str_repr else 'Empty JSONClass Object'

