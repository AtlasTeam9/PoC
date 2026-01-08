from typing import List

class Device(): 
    device_name : str 
    device_assets : List[object]

    def __init__(self, device_name: str, device_assets: List[object]):
        self.device_name = device_name
        self.device_assets = device_assets