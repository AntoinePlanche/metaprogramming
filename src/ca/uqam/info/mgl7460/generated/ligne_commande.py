class ligne_commande:
	def __init__(self, id_produit, quantite):
		self.id_produit = id_produit
		self.quantite = quantite

	def __str__(self) -> str:
		return_string = "ligne_commande["
		return_string = return_string +"id_produit = " + self.id_produit.__str__() + ", "
		return_string = return_string +"quantite = " + self.quantite.__str__() + ", "
		return_string = return_string[:-2] + "]"
		return return_string

