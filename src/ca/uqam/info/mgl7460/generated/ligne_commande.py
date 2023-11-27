class ligne_commande:
    def __init__(self, id_produit: str, quantite: int):
        self.id_produit = id_produit
        self.quantite = quantite

    def __str__(self):
        str_repr = ''
        str_repr += 'id_produit: {id_produit}, ' if self.id_produit is not None else ''
        str_repr += 'quantite: {quantite}, ' if self.quantite is not None else ''
        return str_repr[:-2] if str_repr else 'Empty JSONClass Object'

