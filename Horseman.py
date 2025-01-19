from Units import Units

class Horseman(Units):
    def __init__(self,image, position, lettre='h', cout={'Gold': 20, 'Food': 80, 'Wood': 0}, hp=45, temps_entrainement= 30,attaque=4, vitesse=1.2):
        super().__init__(image,position, lettre, cout, hp, temps_entrainement, attaque, vitesse)