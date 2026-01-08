from device import Device
from position import Position

class Session(): 
    session_id : str 
    device : Device
    position : Position
    results : object

    def __init__(self, session_id : str, device : Device, position : Position, result = {}): 
        self.session_id = session_id
        self.device = device
        self.position = position
        self.results = result