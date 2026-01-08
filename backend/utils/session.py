from .device import Device
from .position import Position
from dataclasses import dataclass
from typing import Dict

@dataclass
class Session(): 
    """ Classe che tiene traccia della sessione """
    session_id : str 
    device : Device
    position : Position
    results : Dict
    finished : bool

    def __init__(self, session_id : str, device : Device, position : Position, result : Dict | None = None, finished : bool = False): 
        self.session_id = session_id
        self.device = device
        self.position = position
        self.results = result if result is not None else {}
        self.finished = finished

    def to_dict(self):
        return {
            "session_id" : self.session_id,
            "device" : self.device.to_dict(),
            "position" : self.position.to_dict(),
            "results" : self.results,
            "finished" : self.finished
        }