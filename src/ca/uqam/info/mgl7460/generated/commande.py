class commande:
	def __init__(self, id):
		self.id = id
		self.table_ligne_commandes = dict()

	def add_ligne_commande(self, a_ligne_commande):
		self.table_ligne_commandes[a_ligne_commande.id_produit] = a_ligne_commande

	def remove_ligne_commande_with_id_produit(self, id_produit):
		self.table_ligne_commandes.pop(id_produit)

	def get_table_ligne_commandes(self):
		return iter(self.table_ligne_commandes.values())

	def get_ligne_commande_with_id_produit(self, id_produit: str):
		return self.table_ligne_commandes[id_produit]

	def __str__(self) -> str:
		return_string = "commande["
		return_string = return_string +"id = " + self.id.__str__() + ", "
		relation_str_ = "table_ligne_commandes" + " = ["
		for key in iter(self.table_ligne_commandes.keys()):
			relation_str_ = relation_str_ + key + " -> " + self.table_ligne_commandes[key].__str__() + ", "
		relation_str_ = relation_str_[:-2] + "]"
		return_string = return_string + relation_str_ + ", "
		return_string = return_string[:-2] + "]"
		return return_string

