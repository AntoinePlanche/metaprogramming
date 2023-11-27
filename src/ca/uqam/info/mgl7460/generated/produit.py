class produit:
    def __init__(self, id: str, nom: str, description: str, prixUnitaire: float):
        self.id = id
        self.nom = nom
        self.description = description
        self.prixUnitaire = prixUnitaire

    def __str__(self):
        str_repr = ''
        str_repr += 'id: {id}, ' if self.id is not None else ''
        str_repr += 'nom: {nom}, ' if self.nom is not None else ''
        str_repr += 'description: {description}, ' if self.description is not None else ''
        str_repr += 'prixUnitaire: {prixUnitaire}, ' if self.prixUnitaire is not None else ''
        return str_repr[:-2] if str_repr else 'Empty JSONClass Object'

