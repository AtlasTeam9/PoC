from dataclasses import dataclass

@dataclass
class Position():
    """ Classe che tiene traccia delle posizioni """
    current_asset_index : int
    current_tree_index : int 
    current_node_id : str 

    def __init__(self, current_asset_index : int, current_tree_index : int, current_node_id : str): 
        self.current_asset_index = current_asset_index
        self.current_tree_index = current_tree_index
        self.current_node_id = current_node_id

    def to_dict(self):
        return {
            "current_asset_index" : self.current_asset_index,
            "current_tree_index" : self.current_tree_index,
            "current_node_id" : self.current_node_id
        }