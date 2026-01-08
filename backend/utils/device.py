from typing import List
from dataclasses import dataclass

@dataclass
class Device(): 
    """ Classe che tiene traccia del Device """
    device_name : str 
    device_assets : List[dict[str, str]]

    def __init__(self, device_name: str, device_assets: List[dict[str, str]]):
        self.device_name = device_name
        self.device_assets = device_assets

    def to_dict(self): 
        return {
            "device_name" : self.device_name,
            "device_assets" : self.device_assets
        }