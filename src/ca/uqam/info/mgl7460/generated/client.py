class client:
	def __init__(self, id, nom, prenom, adresse):
		self.id = id
		self.nom = nom
		self.prenom = prenom
		self.adresse = adresse
		self.liste_commandes = []

	def add_commande(self, a_commande):
		self.liste_commandes.append(a_commande)

	def remove_commande(self, a_commande):
		self.liste_commandes.remove(a_commande)

	def get_liste_commandes(self):
		return iter(self.liste_commandes)

	def __str__(self) -> str:
		return_string = "client["
		return_string = return_string +"id = " + self.id.__str__() + ", "
		return_string = return_string +"nom = " + self.nom.__str__() + ", "
		return_string = return_string +"prenom = " + self.prenom.__str__() + ", "
		return_string = return_string +"adresse = " + self.adresse.__str__() + ", "
		relation_str_ = "liste_commandes" + " = ["
		for related in iter(self.liste_commandes):
			relation_str_ = relation_str_ + related.__str__() + ", "
		relation_str_ = relation_str_[:-2] + "]"
		return_string = return_string + relation_str_ + ", "
		return_string = return_string[:-2] + "]"
		return return_string

