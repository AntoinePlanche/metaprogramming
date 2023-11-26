class Relationship:
        ONE_TO_ONE = 1
        ONE_TO_MANY = 99
        
        #
        def __init__(self, name: str, source_entity: str, destination_entity: str, multiplicity: int, index_field : str = None):
                self.name = name
                self.source_entity = source_entity
                self.destination_entity = destination_entity
                self.multiplicity = Relationship.ONE_TO_ONE
                if (multiplicity > 1 ):
                        self.multiplicity = Relationship.ONE_TO_MANY
                self.index_field = index_field


        def is_indexed(self) -> bool:
                return not (self.index_field == None)


        def __str__(self):
                structure = "List<"
                if (not self.index_field == None):
                        structure = "Map<" + self.index_field+","
                return self.name + " [" + self.source_entity + " -> " + structure + self.destination_entity+ ">]"