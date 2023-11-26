class boutique:
	def __init__(self, nom):
		self.nom = nom
		self.liste_produits = []
		self.liste_clients = []

	def add_produit(self, a_produit):
		self.liste_produits.append(a_produit)

	def remove_produit(self, a_produit):
		self.liste_produits.remove(a_produit)

	def get_liste_produits(self):
		return iter(self.liste_produits)

	def add_client(self, a_client):
		self.liste_clients.append(a_client)

	def remove_client(self, a_client):
		self.liste_clients.remove(a_client)

	def get_liste_clients(self):
		return iter(self.liste_clients)

	def __str__(self) -> str:
		return_string = "boutique["
		return_string = return_string +"nom = " + self.nom.__str__() + ", "
		relation_str_ = "liste_produits" + " = ["
		for related in iter(self.liste_produits):
			relation_str_ = relation_str_ + related.__str__() + ", "
		relation_str_ = relation_str_[:-2] + "]"
		return_string = return_string + relation_str_ + ", "
		relation_str_ = "liste_clients" + " = ["
		for related in iter(self.liste_clients):
			relation_str_ = relation_str_ + related.__str__() + ", "
		relation_str_ = relation_str_[:-2] + "]"
		return_string = return_string + relation_str_ + ", "
		return_string = return_string[:-2] + "]"
		return return_string

