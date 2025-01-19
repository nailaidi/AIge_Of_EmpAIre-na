from Units import Units

class Archer(Units):
    def __init__(self, image, position, lettre='a', cout={'Gold': 45, 'Food': 0, 'Wood': 25}, hp=30, temps_entrainement= 35, attaque=4, vitesse=1):
        super().__init__(image, position, lettre, cout, hp, temps_entrainement, attaque, vitesse)