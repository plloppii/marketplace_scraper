from dataclasses import dataclass

@dataclass
class Listing():
    name: str
    price: str
    location: str
    url: str
    additional_info:str
    image_url: str = None

    
