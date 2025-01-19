from Units import Units
from TileMap import TileMap
from Coordinates import Coordinates
from Villager import Villager
from Swordman import Swordman
from Archer import Archer
from Horseman import Horseman
from Global_image_load import *
from constants import *
import pygame
from pygame.locals import *

class Test:
    def __init__(self):
        self.scroll_speed = 30
        self.tile_map = TileMap()
        self.villager = Villager(villager1,Coordinates(0,0))
        self.villager2 = Villager(villager3,Coordinates(-2,5))
        self.swordman = Swordman(s_man1,Coordinates(3,3))  
        self.horseman = Horseman(h_man1,Coordinates(-3,-3))  
        self.archer = Archer(archer1,Coordinates(-6,-6))
        self.archer2 = Archer(archer2,Coordinates(3,-5)) 
         
        self.tiles={}
    
        self.tile_map.add_unit(self.villager,Villager,4,1,self.tiles)  
        self.tile_map.add_unit(self.villager2,Villager,2,1,self.tiles)   
        self.tile_map.add_unit(self.horseman,Horseman,6,1,self.tiles)   
        self.tile_map.add_unit(self.archer,Archer,3,1,self.tiles)   
        self.tile_map.add_unit(self.archer2,Archer,3,1,self.tiles)   
        self.tile_map.add_unit(self.swordman,Swordman,4,1,self.tiles)

        assert self.tiles!={}, "units not added"  

    def center_camera_on_tile(self):
        center_x = size // 2
        center_y = size // 2
        cart_x = center_x * tile_grass.width_half
        cart_y = center_y * tile_grass.height_half
        iso_x = (cart_x - cart_y)
        iso_y = (cart_x - cart_y) // 2
        cam_x = (iso_x - screen_width // 2) + tile_grass.width_half
        cam_y = -(iso_y + screen_height // 2)
        return cam_x, cam_y
    
    def handle_camera_movement(self, keys):
        min_cam_x, min_cam_y, max_cam_x, max_cam_y = self.calculate_camera_limits()
        cam_x,cam_y=self.center_camera_on_tile()
        speed = self.scroll_speed * 2 if keys[K_LSHIFT] or keys[K_RSHIFT] else self.scroll_speed
        if keys[K_q]:
            cam_x = max(cam_x - speed, min_cam_x)
        if keys[K_d]:
            cam_x = min(cam_x + speed, max_cam_x) 
        if keys[K_z]:
            cam_y = max(cam_y - speed, min_cam_y)  
        if keys[K_s]:
            cam_y = min(cam_y + speed, max_cam_y)
        
    def calculate_camera_limits(self):
        """Calcule les limites de la caméra pour empêcher le défilement hors de la carte."""
        # Taille de la moitié de la carte

        # Calcul des coins en coordonnées cartésiennes
        min_cart_x = -half_size * tile_grass.width_half
        max_cart_x = half_size * tile_grass.width_half
        min_cart_y = -half_size * tile_grass.height_half
        max_cart_y = half_size * tile_grass.height_half

        # Conversion des coins en isométriques
        min_iso_x = min_cart_x - max_cart_y
        max_iso_x = max_cart_x - min_cart_y
        min_iso_y = (min_cart_x + min_cart_y) // 2
        max_iso_y = (max_cart_x + max_cart_y) // 2

        # Ajustement pour la taille de l'écran
        min_cam_x = min_iso_x - (screen_width // 2) + screen_width // 2 + (-5 * tile_grass.width_half)
        max_cam_x = max_iso_x - (screen_width // 2) - screen_width // 2 + 5 * tile_grass.width_half
        min_cam_y = min_iso_y - (screen_height // 2) + screen_height // 2 + (-5 * tile_grass.width_half)
        max_cam_y = max_iso_y - (screen_height // 2) - screen_height // 2 + 5 * tile_grass.width_half

        return min_cam_x, min_cam_y, max_cam_x, max_cam_y
    
    def move_player(self, direction):
        x,y=self.tile_map.position_initiale
        map_data[y][x] = " "
        if direction == 'up' and y > 0:
            y -= 1
        elif direction == 'down' and y < size - 1:
            y += 1
        elif direction == 'left' and x > 0:
            x -= 1
        elif direction == 'right' and x < len(map_data[y]) - 1:
            x += 1
        self.tile_map.position_initiale=(x,y)
       
    def run(self):
        cam_x,cam_y=self.center_camera_on_tile()
        running=True
        while running:
            for event in pygame.event.get():
                if event.type== pygame.QUIT:
                    running=False
                elif event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_z:  # Haut
                        self.tile_map.move_player('up')
                    elif event.type == pygame.K_s:  # Bas
                        self.tile_map.move_player('down')
                    elif event.type == pygame.K_q:  # Gauche
                        self.tile_map.move_player('left')
                    elif event.type == pygame.K_d:  # Droite
                        self.tile_map.move_player('right')

            DISPLAYSURF.fill(BLACK)


            keys = pygame.key.get_pressed()
            self.handle_camera_movement(keys)
            self.tile_map.display_map(cam_x, cam_y)

            for position,players in self.tiles.items():
                for player,units in players.items():
                    for unit in units:
                        unit.diplay_unit(cam_x,cam_y,self.tiles,pygame.time.get_ticks())
            
            fps = int(FPSCLOCK.get_fps())
            fps_text = pygame.font.Font(None, 24).render(f"FPS: {fps}", True, (255, 255, 255))
            DISPLAYSURF.blit(fps_text, (10, 10))
            #print(fps)

            pygame.display.update()
            pygame.display.flip()
            FPSCLOCK.tick(600)
            #print(self.tiles)          