class client:
    def __init__(self, id: str, nom: str, prenom: str, adresse: str):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.adresse = adresse
        self.liste_commandes = []

    def add_commande(self, a_commande):
        self.liste_commandes.append(a_commande)

    def remove_commande(self, a_commande):
        if item in self.liste_commandes:
            self.liste_commandes.remove(a_commande)

    def get_liste_commandes(self):
        return iter(self.liste_commandes)

    def __str__(self):
        str_repr = ''
        str_repr += 'id: {id}, ' if self.id is not None else ''
        str_repr += 'nom: {nom}, ' if self.nom is not None else ''
        str_repr += 'prenom: {prenom}, ' if self.prenom is not None else ''
        str_repr += 'adresse: {adresse}, ' if self.adresse is not None else ''
        str_repr += '    commande: ' + str(list(self.commande)) + '\n'
        return str_repr[:-2] if str_repr else 'Empty JSONClass Object'

