class produit:
    def __init__(self, id: str, nom: str, description: str, prixUnitaire: float):
        self.id = id
        self.nom = nom
        self.description = description
        self.prixUnitaire = prixUnitaire

    def __str__(self) -> str:
        return_string = "produit["
        return_string += "id = " + self.id.__str__() + ", " 
        return_string += "nom = " + self.nom.__str__() + ", " 
        return_string += "description = " + self.description.__str__() + ", " 
        return_string += "prixUnitaire = " + self.prixUnitaire.__str__() + ", " 
        return_string = return_string[:-2] + "]"
        return return_string
