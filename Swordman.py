from Units import Units

class Swordman(Units):
    def __init__(self, image, position, lettre='s', cout={'Gold': 20, 'Food': 50, 'Wood': 0}, hp=40, temps_entrainement= 20,attaque=4, vitesse=0.9):
        super().__init__(image, position, lettre, cout, hp, temps_entrainement, attaque, vitesse)