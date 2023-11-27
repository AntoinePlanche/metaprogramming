class commande:
    def __init__(self, id: str):
        self.id = id
        self.table_ligne_commandes = {}

    def add_ligne_commande(self, a_ligne_commande):
        self.table_ligne_commandes[a_ligne_commande.id_produit] = item

    def remove_ligne_commande_with_id_produit(self, id_produit):
        if id_produit in self.table_ligne_commandes:
            self.table_ligne_commandes.pop(id_produit)

    def get_table_ligne_commandes(self):
        return iter(self.table_ligne_commandes.values())

    def get_ligne_commande_with_id_produit(self, id_produit : str):
        return self.table_ligne_commandes.get(id_produit, None)

    def __str__(self):
        str_repr = ''
        str_repr += 'id: {id}, ' if self.id is not None else ''
        str_repr += '    ligne_commande: ' + str({key: value for key, value in self.ligne_commande.items()}) + '\n'
        return str_repr[:-2] if str_repr else 'Empty JSONClass Object'

