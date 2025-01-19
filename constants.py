import pygame
import numpy as np
import curses


class Tile:
    def __init__(self, image_path, width, height):
        # Chargez l'image et appliquez le redimensionnement en width x height pixels
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

        # Stockez les dimensions spécifiées
        self.width = width
        self.height = height
        self.width_half = width // 2
        self.height_half = height // 2


pygame.init()


info = pygame.display.Info()
screen_width = info.current_w #-500  # Largeur de l'écran
screen_height = info.current_h #-500  # Hauteur de l'écran

action_a_executer=[]



DISPLAYSURF = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
FPSCLOCK = pygame.time.Clock()
FPSCLOCK.tick(60)

size = 120
half_size = size//2

barre_width = screen_width//2.5  # Largeur de la barre
barre_height = screen_height//13.5 # Hauteur de la barre

barre_units_width= screen_width//2.5
barre_units_height = screen_height//27


tile_grass = Tile('images/cube_grass.png', 64, 64)
tile_wood = Tile('images/cube_tree.png', 64, 128)
tile_gold = Tile('images/cube_rocky2.png', 64, 64)



swordsman_image = pygame.image.load("images/epeiste.png")  # Remplace "swordsman.png" par le nom de ton fichier
swordsman_image = pygame.transform.scale(swordsman_image, (32, 32))

unit_tile="images/img_1.webp"
unit_image=  pygame.image.load(unit_tile).convert_alpha()

#unit_images = [
#    pygame.image.load("images/img_1.webp").convert_alpha(),
#    pygame.image.load("images/sprites/Unit/villager/img_0.webp").convert_alpha(),
#]
current_image_index = 0

compteurs_joueurs = {}

ressources_dict = {
    'W':{
        'image': Tile('images/cube_tree.png', 64, 128),
        'quantite' : 100,
    },
    'G':{
            'image': Tile('images/cube_rocky2.png', 64, 64),
            'quantite' : 800,
        }
}

units_dict = {
    'v': {
        'image': Tile("images/sprites/Unit/villager/img_0.webp", 32, 32),
        'cout': {'G': 0, 'f': 50, 'W': 0},
        'hp': 25,
        'temps_entrainement': 25,
        'attaque': 2,
        'vitesse': 0.8,
        'capacité' : 20
    },
    's': {  # Épéiste
        'image': Tile("images/sprites/Unit/swordman/img_0.webp", 32, 32),
        'cout': {'G': 20, 'f': 50, 'W': 0},
        'hp': 40,
        'temps_entrainement': 20,
        'attaque': 4,
        'vitesse': 0.9
    },
    'h': {  # Cavalier
        'image': Tile("images/sprites/Unit/horseman/img_0.webp", 32, 32),
        'cout': {'G': 20, 'f': 80, 'W': 0},
        'hp': 45,
        'temps_entrainement': 30,
        'attaque': 4,
        'vitesse': 1.2
    },
    'a': {  # Archer
        'image': Tile("images/sprites/Unit/archer/img_0.webp", 30, 30),
        'cout': {'G': 45, 'f': 0, 'W': 25},
        'hp': 30,
        'temps_entrainement': 35,
        'attaque': 4,
        'vitesse': 1
    }
}

builds_dict = {
    'T': {
        'tile': Tile("images/Town_Center.webp", 200, 128),
        'taille': 4,
        'cout': {'G': 0, 'W': 350, 'f': 0},
        'build_time': 5,  # Temps en secondes
        'hp': 10
    },
    'H': {
        'tile': Tile("images/House.webp", 90, 70),
        'taille': 2,
        'cout': {'G': 0, 'W': 25, 'f': 0},
        'build_time': 25,
        'hp': 200
    },
    'C': {
        'tile': Tile("images/Camp.png", 90, 70),
        'taille': 2,
        'cout': {'G': 0, 'W': 100, 'f': 0},
        'build_time': 25,
        'hp': 200
    },
    'F': {
        'tile': Tile("images/Farm - Copie.png", 60, 60),
        'taille': 2,
        'cout': {'G': 0, 'W': 60, 'f': 0},
        'build_time': 10,
        'hp': 100,
        'quantite': 300
    },
    'B': {
        'tile': Tile("images/Barracks.png", 128, 100),
        'taille': 3,
        'cout': {'G': 0, 'W': 175, 'f': 0},
        'build_time': 50,
        'hp': 500
    },
    'S': {
        'tile': Tile("images/Stable.png", 128, 100),
        'taille': 3,
        'cout': {'G': 0, 'W': 175, 'f': 0},
        'build_time': 50,
        'hp': 500
    },
    'A': {
        'tile': Tile("images/Archery Range.png", 128, 100),
        'taille': 3,
        'cout': {'G': 0, 'W': 175, 'f': 0},
        'build_time': 50,
        'hp': 500
    },
    'K': {
        'tile': Tile("images/Keep.png", 64, 64),
        'taille': 1,
        'cout': {'G': 125, 'W': 35, 'f': 0},
        'build_time': 80,
        'hp': 800
    }
}



tuiles = {}
compteurs_unites = {}

GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128,128,128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BROWN = (139, 69, 19)
PINK = (255, 105, 180)

PLAYER_COLORS = {
    "joueur_1": RED,       # Rouge
    "joueur_2": GREEN,     # Vert
    "joueur_3": YELLOW,    # Jaune
    "joueur_4": BLUE,      # Bleu
    "joueur_5": ORANGE,    # Orange
    "joueur_6": PURPLE,    # Violet
    "joueur_7": CYAN,      # Cyan
    "joueur_8": MAGENTA,   # Magenta
    "joueur_9": BROWN,     # Marron
    "joueur_10": PINK      # Vert clair
}

MAP_COLORS = {
    "joueur_1": (1, curses.COLOR_BLACK),
    "joueur_2": (2, curses.COLOR_BLACK),
    "joueur_3": (3, curses.COLOR_BLACK),
    "joueur_4": (4, curses.COLOR_BLACK),
    "joueur_5": (202, curses.COLOR_BLACK),
    "joueur_6": (129, curses.COLOR_BLACK),
    "joueur_7": (51, curses.COLOR_BLACK),
    "joueur_8": (201, curses.COLOR_BLACK),
    "joueur_9": (94, curses.COLOR_BLACK),
    "joueur_10": (218, curses.COLOR_BLACK),
}

map_data = np.full((size, size), " ")