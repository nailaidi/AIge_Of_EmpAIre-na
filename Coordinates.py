from TileMap import *
from constants import *

class Coordinates:
    def __init__(self):
        self.x=0
        self.y=0

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def to_iso(self,x, y, cam_x, cam_y, unit_tile):
        half_size = size // 2  # Assurez-vous que la taille de la carte est correctement définie

        offset_x = tile_grass.width_half - unit_tile.get_width() // 2
        offset_y = tile_grass.height_half - unit_tile.get_height() // 2

        centered_col = x - half_size  # Décalage en X
        centered_row = y - half_size  # Décalage en Y

        # Conversion en coordonnées isométriques
        cart_y = centered_col * tile_grass.width_half
        cart_x = centered_row * tile_grass.height_half

        iso_x = (cart_x - cart_y) - cam_x -70#+ offset_x
        iso_y = (cart_x + cart_y) / 2 - cam_y -81 #- offset_y

        #iso_x = (int(current_y - current_x)) * tile_grass.width - cam_x
        #iso_y = (int(current_x + current_y)//2) * tile_grass.height - cam_y
        #print(cart_x,cart_y)
        #print(iso_x, iso_y)
        return iso_x,iso_y