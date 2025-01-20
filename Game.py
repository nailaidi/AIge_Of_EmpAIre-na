import pygame
import sys
import json
from pygame.locals import *

import Units
from constants import *
from TileMap import TileMap
from Barre_ressource import Barre_ressources
from Units import Unit
from Buildings import Buildings
from Page_HTML import Page_HTML
from Save_and_load import Save_and_load
from Initialisation_Compteur import Initialisation_Compteur
from Recolte_ressources import Recolte_ressources
import curses
import keyboard
import time
import threading
import webbrowser
import os
from colorama import Fore, Style
from collections import deque


class Game:
    """Classe principale gérant le jeu."""

    def __init__(self):

        # MAP
        self.scroll_speed = 30
        self.tile_map = None
        self.tile_map = TileMap()
        self.cam_x, self.cam_y = self.center_camera_on_tile()

        # MINIMAP
        self.mini_map_size_x = 490  # Largeur de la mini-carte
        self.mini_map_size_y = 270  # Hauteur de la mini-carte  # Taille carrée de la mini-carte
        self.mini_map_scale = 4  # Échelle de réduction de la mini-carte
        self.cam_mini_x, self.cam_mini_y = self.center_camera_on_tile()

        # BARRE JOUEURS

        # MENU DEPART

        self.selected_option = None
        self.menu_active = True
        self.selected_unit = None
        self.selected_map = None
        self.joueur = 0
        self.compteur = compteurs_joueurs

        self.Initialisation_compteur = Initialisation_Compteur()

        self.n = 2  # Définition du nombre de joueurs
        self.plus = None
        self.moins = None

        # TERMINAL

        self.terminal_x = 0
        self.terminal_y = 0
        self.terminal_active = False
        self.position_initiale = (size // 2, size // 2)  # Position initiale du joueur

        # UNITS
        # self.swordsman = Units.Swordsman()
        self.unit = Unit()
        self.tiles = {}
        self.test = deque()

        # RECOLTE_RESSOURCES
        self.recolte = Recolte_ressources()

        # BUILDS
        self.buildings = Buildings()

        # Page HTML
        self.page_html = Page_HTML()

        # Save and Load
        self.save_and_load = Save_and_load()

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

    def center_camera_on_tile(self):
        """Centre la caméra sur la tuile centrale de la carte."""
        center_x = size // 2
        center_y = size // 2

        # Conversion des coordonnées de la tuile centrale en isométriques
        tile_width_half = tile_grass.width_half
        tile_height_half = tile_grass.height_half
        cart_x = center_x * tile_width_half
        cart_y = center_y * tile_height_half
        iso_x = (cart_x - cart_y)
        iso_y = (cart_x - cart_y) // 2

        cam_x = (iso_x - screen_width // 2) + tile_width_half
        cam_y = -(iso_y + screen_height // 2)

        return cam_x, cam_y

    def show_menu(self):
        """Affiche un menu pour choisir la carte et charger les données sauvegardées."""
        font = pygame.font.Font(None, 74)
        small_font = pygame.font.Font(None, 36)

        fond_image = pygame.image.load('images/test4.jpg')
        fond_image = pygame.transform.scale(fond_image, (screen_width, screen_height))
        DISPLAYSURF.blit(fond_image, (0, 0))

        menu_text = font.render("Menu Principal", True, BLACK)
        menu_text_rect = menu_text.get_rect(center=(screen_width // 2, 100))
        DISPLAYSURF.blit(menu_text, menu_text_rect)

        card_color1 = YELLOW if self.selected_unit == "Lean" else BLACK
        card_color2 = YELLOW if self.selected_unit == "Mean" else BLACK
        card_color3 = YELLOW if self.selected_unit == "Marines" else BLACK
        card_color4 = YELLOW if self.selected_map == "Map 1" else BLACK
        card_color5 = YELLOW if self.selected_map == "Map 2" else BLACK

        card1_text = small_font.render("Lean", True, card_color1)
        card2_text = small_font.render("Mean", True, card_color2)
        card3_text = small_font.render("Marines", True, card_color3)
        card4_text = small_font.render("Map 1", True, card_color4)
        card5_text = small_font.render("Map 2", True, card_color5)
        start_text = small_font.render("Commencer la Partie", True, GREEN)

        self.card1_rect = card1_text.get_rect(topleft=(screen_width // 2 - 150, 200))
        self.card2_rect = card2_text.get_rect(topleft=(screen_width // 2 - 150, 250))
        self.card3_rect = card3_text.get_rect(topleft=(screen_width // 2 - 150, 300))
        self.card4_rect = card4_text.get_rect(topleft=(screen_width // 2 + 50, 200))
        self.card5_rect = card5_text.get_rect(topleft=(screen_width // 2 + 50, 250))

        DISPLAYSURF.blit(card1_text, self.card1_rect.topleft)
        DISPLAYSURF.blit(card2_text, self.card2_rect.topleft)
        DISPLAYSURF.blit(card3_text, self.card3_rect.topleft)
        DISPLAYSURF.blit(card4_text, self.card4_rect.topleft)
        DISPLAYSURF.blit(card5_text, self.card5_rect.topleft)

        mini_texte = pygame.font.Font(None, 24)
        box_text = mini_texte.render(f"{self.n} joueurs", True, BLACK)
        box_text_render = box_text.get_rect(topleft=(screen_width * 0.48, 400))
        rectangle_width = box_text_render.width + 15 * 2  # Largeur du texte + marge gauche/droite
        rectangle_height = box_text_render.height + 10 * 2  # Hauteur du texte + marge haut/bas

        rectangle_topleft = (box_text_render.x - 10, box_text_render.y - 10)

        pygame.draw.rect(DISPLAYSURF, GRAY, pygame.Rect(rectangle_topleft, (rectangle_width, rectangle_height)))
        DISPLAYSURF.blit(box_text, box_text_render)

        plus_text = mini_texte.render("+", True, BLACK)
        plus_text_render = plus_text.get_rect()
        rectangle_plus_width = plus_text_render.width + 10 * 2  # Largeur du texte + marge gauche/droite
        rectangle_plus_height = plus_text_render.height + 10 * 2  # Hauteur du texte + marge haut/bas
        rectangle_plus_topleft = (
            box_text_render.x + 108, box_text_render.y + (box_text_render.height - rectangle_plus_height) // 2)
        pygame.draw.rect(DISPLAYSURF, WHITE,
                         pygame.Rect(rectangle_plus_topleft, (rectangle_plus_width, rectangle_plus_height)))
        plus_text_render.center = (
            rectangle_plus_topleft[0] + rectangle_plus_width // 2,
            rectangle_plus_topleft[1] + rectangle_plus_height // 2)

        DISPLAYSURF.blit(plus_text, plus_text_render)

        self.plus = pygame.Rect(rectangle_plus_topleft, (rectangle_plus_width, rectangle_plus_height))

        minus_text = mini_texte.render("-", True, BLACK)
        minus_text_render = minus_text.get_rect()
        rectangle_minus_width = minus_text_render.width + 10 * 2  # Largeur du texte + marge gauche/droite
        rectangle_minus_height = minus_text_render.height + 10 * 2  # Hauteur du texte + marge haut/bas
        rectangle_minus_topleft = (
            box_text_render.x - 50, box_text_render.y + (box_text_render.height - rectangle_minus_height) // 2)
        pygame.draw.rect(DISPLAYSURF, WHITE,
                         pygame.Rect(rectangle_minus_topleft, (rectangle_minus_width, rectangle_minus_height)))
        minus_text_render.center = (
            rectangle_minus_topleft[0] + rectangle_minus_width // 2,
            rectangle_minus_topleft[1] + rectangle_minus_height // 2)

        DISPLAYSURF.blit(minus_text, minus_text_render)

        self.moins = pygame.Rect(rectangle_minus_topleft, (rectangle_minus_width, rectangle_minus_height))

        self.start_rect = start_text.get_rect(center=(screen_width // 2, 500))
        DISPLAYSURF.blit(start_text, self.start_rect.topleft)

        pygame.display.update()

    def ajouter_unite(self, joueur, type_unite, id_unite, position, hp, status="libre"):
        # Vérifie si la position existe dans map_data, sinon initialise une entrée.
        if position not in tuiles:
            tuiles[position] = {'unites': {}}

        # Vérifie si le joueur existe dans la position, sinon initialise une entrée.
        if joueur not in tuiles[position]['unites']:
            tuiles[position]['unites'][joueur] = {}

        # Vérifie si le type d'unité existe pour ce joueur, sinon initialise une entrée.
        if type_unite not in tuiles[position]['unites'][joueur]:
            tuiles[position]['unites'][joueur][type_unite] = {}

        # Ajoute ou met à jour l'unité.
        tuiles[position]['unites'][joueur][type_unite][id_unite] = {
            'HP': hp,
            'Status': status
        }

        print(f"Unité ajoutée: {tuiles[position]['unites'][joueur][type_unite][id_unite]}")

    def handle_menu_events(self, event):
        """Gère les événements liés au menu principal."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Vérifier la sélection des unités
            x, y = event.pos

            # Clic sur la flèche +
            if self.plus.collidepoint(x, y):
                if self.n < 10:  # Limiter à 10 joueurs
                    self.n += 1

            # Clic sur la flèche -
            elif self.moins.collidepoint(x, y):
                if self.n > 2:  # Limiter à 2 joueurs
                    self.n -= 1

            if self.card1_rect.collidepoint(event.pos):
                self.selected_unit = "Lean"
                self.Initialisation_compteur.initialize_resources(self.selected_unit, self.n)
            elif self.card2_rect.collidepoint(event.pos):
                self.selected_unit = "Mean"
                self.Initialisation_compteur.initialize_resources(self.selected_unit, self.n)
            elif self.card3_rect.collidepoint(event.pos):
                self.selected_unit = "Marines"
                self.Initialisation_compteur.initialize_resources(self.selected_unit, self.n)

            elif self.card4_rect.collidepoint(event.pos):
                self.selected_map = "Map 1"
            elif self.card5_rect.collidepoint(event.pos):
                self.selected_map = "Map 2"

            elif self.start_rect.collidepoint(event.pos) and self.selected_unit and self.selected_map:
                self.menu_active = False
                if self.selected_map == 'Map 1':
                    self.tile_map.mode("patches")
                else:
                    self.tile_map.mode("middle")

                self.tile_map.add_wood_patches()

                self.tile_map.render(DISPLAYSURF, self.cam_x, self.cam_y)
                # pygame.display.update()
                with open("test.txt", 'w') as f:
                    for row in map_data:
                        # Convertir chaque ligne en une chaîne de caractères avec des espaces entre les éléments
                        f.write(" ".join(str(cell) for cell in row) + "\n")

                position = self.unit.placer_joueurs_cercle(self.n, 40, size // 2, size // 2)
                self.Initialisation_compteur.initialize_resources(self.selected_unit, self.n)


                self.buildings.initialisation_compteur(position)


                self.unit.initialisation_compteur(position)
                self.draw_mini_map(DISPLAYSURF)
                print(tuiles)



    def draw_mini_map(self, display_surface):
        losange_surface = pygame.Surface((self.mini_map_size_x, self.mini_map_size_y), pygame.SRCALPHA)
        losange_surface.fill((0, 0, 0, 0))  # Remplir de transparent

        mini_map_surface = pygame.Surface((self.mini_map_size_x, self.mini_map_size_y), pygame.SRCALPHA)
        mini_map_surface.fill((0, 0, 0, 0))  # Fond transparent
        tile_width_half = 1
        tile_height_half = 1

        for row in range(size):
            for col in range(size):
                tile = tuiles.get((row, col), {})  # Récupérer les données de la tuile ou un dictionnaire vide
                color = (34, 139, 34)  # Vert par défaut pour les tuiles vides

                # Vérification des ressources
                if "ressources" in tile:
                    ressource = tile["ressources"]
                    if ressource == "G":
                        color = (255, 215, 0)  # Jaune pour l'or
                    elif ressource == "W":
                        color = (139, 69, 19)  # Marron pour le bois

                # Vérification des bâtiments
                elif "batiments" in tile:
                    color = (128, 128, 128)  # Gris pour les bâtiments

                # Vérification des unités
                elif "unites" in tile:
                    color = (255, 0, 0)  # Rouge pour les unités
                else:
                    color = (34, 139, 34)

                centered_col = col - (size // 2)
                centered_row = row - (size // 2)

                cart_x = centered_col * tile_width_half * self.mini_map_scale
                cart_y = centered_row * tile_height_half * self.mini_map_scale

                iso_x = (cart_x - cart_y) / 2 + self.mini_map_size_x // 2
                iso_y = (cart_x + cart_y) / 4 + self.mini_map_size_y // 2

                # Dessin de la tuile sur la mini-carte
                pygame.draw.rect(mini_map_surface, color, (iso_x, iso_y, self.mini_map_scale, self.mini_map_scale))

        losange_points = [
            (self.mini_map_size_x // 2 + 2, 12),
            (self.mini_map_size_x + 1, self.mini_map_size_y // 2),
            (self.mini_map_size_x // 2 + 2, self.mini_map_size_y - 12),
            (2, self.mini_map_size_y // 2)
        ]

        pygame.draw.polygon(losange_surface, (0, 0, 0), losange_points, 2)  # Contour noir de 2 pixels
        losange_surface.blit(mini_map_surface, (0, 0))  # Positionner la mini-carte sur le losange

        # Afficher le losange sur l'écran principal
        display_surface.blit(losange_surface, (
            screen_width - self.mini_map_size_x - 10, screen_height - self.mini_map_size_y - 10))

    def handle_camera_movement(self, keys):
        min_cam_x, min_cam_y, max_cam_x, max_cam_y = self.calculate_camera_limits()
        speed = self.scroll_speed * 2 if keys[K_LSHIFT] or keys[K_RSHIFT] else self.scroll_speed

        if keys[K_q]:
            self.cam_x = max(self.cam_x - speed, min_cam_x)  # Déplace à gauche
        if keys[K_d]:
            self.cam_x = min(self.cam_x + speed, max_cam_x)  # Déplace à droite
        if keys[K_z]:
            self.cam_y = max(self.cam_y - speed, min_cam_y)  # Déplace vers le haut
        if keys[K_s]:
            self.cam_y = min(self.cam_y + speed, max_cam_y)  # Déplace vers le bas

    def handle_mini_map_click(self, mouse_pos):
        """Gère le clic sur la mini-carte et déplace la caméra."""
        # Définir la zone de la mini-carte
        mini_map_rect = pygame.Rect(screen_width - self.mini_map_size_x - 10,
                                    screen_height - self.mini_map_size_y - 10,
                                    self.mini_map_size_x, self.mini_map_size_y)

        if mini_map_rect.collidepoint(mouse_pos):
            # Calculer les coordonnées dans la mini-carte
            mini_map_x = mouse_pos[0] - (screen_width - self.mini_map_size_x - 10)
            mini_map_y = mouse_pos[1] - (screen_height - self.mini_map_size_y - 10)

            scale_x = size * (tile_grass.width_half * 2) / self.mini_map_size_x
            scale_y = size * tile_grass.height_half / self.mini_map_size_y

            world_x = int((mini_map_x - self.mini_map_size_x // 2) * scale_x)
            world_y = int((mini_map_y - self.mini_map_size_y // 2) * scale_y)

            self.cam_x = world_x - screen_width // 2
            self.cam_y = world_y - screen_height // 2

    def init_player_colors(self):
        curses.start_color()
        curses.use_default_colors()

        for idx, (player, (fg, bg)) in enumerate(MAP_COLORS.items(), start=1):
            curses.init_pair(idx, fg, bg)

    def get_player_color(self, player_name):
        player_index = list(MAP_COLORS.keys()).index(player_name) + 1
        return curses.color_pair(player_index)

    def draw_map_in_terminal(self, stdscr):
        self.init_player_colors()
        stdscr.clear()
        stdscr.nodelay(1)
        stdscr.timeout(500)
        curses.init_color(12, 120, 120, 120)
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_WHITE)

        map_rows = size
        map_cols = size

        while self.terminal_active:
            stdscr.clear()
            max_rows, max_cols = stdscr.getmaxyx()
            player_x, player_y = self.tile_map.position_initiale
            view_top = max(0, min(player_x - max_rows // 2, map_rows - max_rows))
            view_left = max(0, min(player_y - max_cols // 2, map_cols - max_cols))

            for row in range(view_top, min(view_top + max_rows, map_rows)):
                for col in range(view_left, min(view_left + max_cols, map_cols)):

                    if (row, col) == (player_x, player_y):
                        stdscr.addstr(row - view_top, col - view_left, "P",
                                      curses.color_pair(12))  # Rouge pour le joueur
                    else:

                        tile = tuiles.get((row, col), {})
                        char = " "  # Espace vide par défaut
                        color = 0  # Pas de couleur par défaut

                        # Déterminer le caractère à afficher pour cette tuile

                        if "batiments" in tile:
                            for joueur, batiments_joueur in tile["batiments"].items():
                                # print(row, col ,batiments_joueur)
                                for batiment_type, details in batiments_joueur.items():

                                    if batiment_type == "T":
                                        char = "T"
                                        color = self.get_player_color(joueur)
                                    elif batiment_type == "H":
                                        char = "H"
                                        color = self.get_player_color(joueur)
                                    elif batiment_type == "C":
                                        char = "C"
                                        color = self.get_player_color(joueur)
                                    elif batiment_type == "f":
                                        char = "f"
                                        color = self.get_player_color(joueur)
                                    elif batiment_type == "B":
                                        char = "B"
                                        color = self.get_player_color(joueur)
                                    elif batiment_type == "S":
                                        char = "S"
                                        color = self.get_player_color(joueur)
                                    elif batiment_type == "A":
                                        char = "A"
                                        color = self.get_player_color(joueur)
                                    elif batiment_type == "K":
                                        char = "K"
                                        color = self.get_player_color(joueur)
                                    else:
                                        char = " "
                                    break
                                break


                        elif "unites" in tile:
                            for joueur, unites_joueur in tile["unites"].items():
                                for unite_type, details in unites_joueur.items():
                                    if unite_type == "v":
                                        char = "v"
                                        color = self.get_player_color(joueur)
                                        # print(color)
                                    elif unite_type == "a":
                                        char = "a"
                                        color = self.get_player_color(joueur)
                                    elif unite_type == "h":
                                        char = "h"
                                        color = self.get_player_color(joueur)
                                    elif unite_type == "s":
                                        char = "s"
                                        color = self.get_player_color(joueur)
                                    else:
                                        char = " "

                                    break
                                break

                        # Déterminer les ressources
                        elif "ressources" in tile:
                            ressource = tile["ressources"]
                            if ressource == "G":
                                char = "G"
                            elif ressource == "W":
                                char = "W"
                            else:
                                char = " "
                        if 0 <= row - view_top < max_rows and 0 <= col - view_left < max_cols:
                            if char is None:
                                char = " "  # Par défaut, espace vide
                            elif not isinstance(char, str):
                                char = str(char)  # Assurez-vous que char est une chaîne

                            # Affichage avec ou sans couleur
                            try:
                                if color != 0:
                                    stdscr.addstr(row - view_top, col - view_left, char, color)
                                else:
                                    stdscr.addstr(row - view_top, col - view_left, char)
                            except curses.error as e:
                                print(f"Erreur à ({row}, {col}): {e}")
            stdscr.refresh()

            # Gestion des touches pour déplacer le joueur
            key = stdscr.getch()  # Attendre une touche
            if key == ord('q'):  # Haut
                self.tile_map.move_player('up')
            elif key == ord('d'):  # Bas
                self.tile_map.move_player('down')
            elif key == ord('z'):  # Gauche
                self.tile_map.move_player('left')
            elif key == ord('s'):  # Droite
                self.tile_map.move_player('right')
            elif key == ord('j'):
                self.buildings.decrementer_hp_batiments()
            elif key == ord('k'):
                joueur = 'joueur_1'
                type_unite = 'v'
                id_unite = 0

                position = self.recolte.trouver_plus_proche_ressource(joueur, type_unite, id_unite, ressource='W')
                self.unit.deplacer_unite(joueur='joueur_1',
                                         type_unite='v',
                                         id_unite=0,
                                         nouvelle_position=position,
                                         )

                self.recolte.recolter_ressource_plus_proche_via_trouver(joueur, type_unite,
                                                                        id_unite, ressource='W', posress=position)
            elif key == ord('-'):
                self.unit.decrementer_hp_unite()

            elif key == 9:  # Code ASCII pour Tab
                file_path = self.page_html.generate_html(tuiles)
                browser = webbrowser.get("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s")
                browser.open(f"file:///{file_path}")

            elif key == ord('t'):
                self.ouvrir_terminal()
            elif key == ord(' '):
                self.sauvegarde_manager.sauvegarder_jeu(self.tuiles, self.compteurs_unites)  # Appeler la sauvegarde


            time.sleep(0.1)  # Pause pour éviter d'utiliser trop de CPU

    def ouvrir_terminal(self):
        if self.terminal_active:
            # Ferme le terminal
            self.terminal_active = False
            # print("avant",self.cam_x, self.cam_y)

            # Récupération de la position du joueur
            y, x = self.tile_map.position_initiale  # Assurez-vous de l'ordre ici (col, row)
            half_size = size // 2  # Assurez-vous que la taille de la carte est correctement définie

            # Décalage centré pour le joueur
            centered_col = y - half_size
            centered_row = x - half_size

            # Conversion en coordonnées isométriques
            cart_x = centered_row * tile_grass.width_half
            cart_y = centered_col * tile_grass.width_half

            iso_x = cart_x - cart_y  # Ne pas soustraire cam_x ici
            iso_y = (cart_x + cart_y) / 2  # Ne pas soustraire cam_y ici

            self.cam_x = iso_x - (screen_width // 2) + tile_grass.width_half
            self.cam_y = iso_y - (screen_height // 2)

            print("Caméra après ajustement:", self.cam_x, self.cam_y)

        else:

            iso_x = self.cam_x + (screen_width // 2) - tile_grass.width_half
            iso_y = self.cam_y + (screen_height // 2)

            # Conversion des coordonnées isométriques en coordonnées cartésiennes
            cart_x = (iso_x + 2 * iso_y) / 2
            cart_y = (2 * iso_y - iso_x) / 2  # Formule inverse pour obtenir cart_y

            half_size = size // 2  # Taille centrée de la carte

            centered_col = int(cart_y / tile_grass.height_half)  # Indice de la colonne
            centered_row = int(cart_x / tile_grass.width_half)  # Indice de la ligne

            # Récupération des coordonnées de la matrice
            y = centered_row + half_size  # Ajustement en fonction de half_size
            x = centered_col + half_size  # Ajustement en fonction de half_size

            self.tile_map.position_initiale = x, y
            # Ouvre le terminal dans un nouveau thread
            self.terminal_active = True
            terminal_thread = threading.Thread(target=curses.wrapper, args=(self.draw_map_in_terminal,))
            terminal_thread.daemon = True
            terminal_thread.start()


    def run(self):
        """Boucle principale du jeu."""
        running = True
        pygame.display.set_caption("Carte et mini-carte")

        while running:
            dt = FPSCLOCK.tick(600) / 1000

            events = pygame.event.get()
            for event in events:
                if (event.type == KEYDOWN and event.key == K_ESCAPE) or event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_F1:
                    self.Initialisation_compteur.f1_active = not self.Initialisation_compteur.f1_active

                if event.type == KEYDOWN and event.key == K_F2:
                    self.Initialisation_compteur.f2_active = not self.Initialisation_compteur.f2_active

                if event.type == KEYDOWN and event.key == K_F3:
                    self.Initialisation_compteur.f3_active = not self.Initialisation_compteur.f3_active

                if event.type == KEYDOWN and event.key == K_t:
                    self.ouvrir_terminal()

                if event.type == KEYDOWN and event.key == K_u:
                    # self.unit.creation_unite('v', 'joueur_1')
                    taille = builds_dict["f"]['taille']
                    in_game = 1
                    self.buildings.ajouter_batiment("joueur_2", "f", 60, 60, taille, tuiles, in_game)
                if event.type == KEYDOWN and event.key == K_y:
                    self.unit.creation_unite('a', 'joueur_1')
                    self.unit.creation_unite('v', 'joueur_1')
                    self.unit.creation_unite('h', 'joueur_1')
                    self.unit.creation_unite('s', 'joueur_1')
                    
                if event.type == KEYDOWN and event.key == K_g:
                    position_a = None
                    joueur_a = 'joueur_2'
                    type_a = 'T'
                    id_a = 'T0'
                    for pos, data in tuiles.items():
                        if 'unites' in data and joueur_a in data['unites'] and type_a in data['unites'][joueur_a]:
                            print(data['unites'][joueur_a])
                            if id_a in data['unites'][joueur_a][type_a]:
                                position_a = pos
                                break


                    for pos, data in tuiles.items():
                        if 'batiments' in data and joueur_a in data['batiments'] and type_a in data['batiments'][joueur_a]:
                            #print("ok")
                            if data['batiments'][joueur_a][type_a]['id'] == id_a:
                                print("ok")
                                position_a = pos  # Récupérer la position du bâtiment
                                print(f"Bâtiment trouvé à la position : {position_a}")
                                break
                    x,y = position_a
                    new_pos = (x-units_dict['v'].get('range', 1),y)
                    print(new_pos)

                    self.unit.deplacer_unite('joueur_1','a',0,new_pos )

                if event.type == KEYDOWN and event.key == K_f:
                    self.unit.attack_building('joueur_1','a',0, 'joueur_2','T','T0')

                if event.type == KEYDOWN and event.key == K_h:


                    joueur = 'joueur_1'
                    type_unite = 'v'
                    id_unite = 0

                    position = self.recolte.trouver_plus_proche_ressource(joueur, type_unite, id_unite, ressource='F')
                    print(position)

                    self.unit.deplacer_unite(joueur, type_unite, id_unite, position)
                    action_a_executer.append(
                        lambda posress=position: self.recolte.recolter_ressource_plus_proche_via_trouver(joueur, type_unite, id_unite, posress=posress))
                    def action_apres_deplacement():
                        if int(tuiles[self.unit.position]['unites'][joueur][type_unite][id_unite]['capacite']) == 20:
                            pos_batiment = self.recolte.trouver_plus_proche_batiment(joueur, type_unite, id_unite)
                            if pos_batiment:

                                self.unit.deplacer_unite(joueur, type_unite, id_unite, pos_batiment)

                    action_a_executer.append(action_apres_deplacement)

                    def deposer_ressources_in_batiment():
                            quantite = 20
                            ressource = 'f'
                            self.recolte.deposer_ressources(quantite, joueur, type_unite, id_unite, ressource)

                    action_a_executer.append(deposer_ressources_in_batiment)


                if event.type == KEYDOWN and event.key == K_KP_MINUS:  # Touche "-"
                    self.unit.decrementer_hp_unite()

                if event.type == KEYDOWN and event.key == K_KP_PLUS:  # Touche "-"
                    self.buildings.decrementer_hp_batiments()

                if event.type == KEYDOWN and event.key == K_F11:
                    self.save_and_load.sauvegarder_jeu(tuiles, compteurs_joueurs)

                if event.type == KEYDOWN and event.key == K_F12:
                    fichier = self.save_and_load.choisir_fichier_sauvegarde()
                    if fichier:
                        nouvelles_tuiles, nouveaux_compteurs = self.save_and_load.charger_jeu(fichier)
                        if nouvelles_tuiles and nouveaux_compteurs:
                            tuiles.clear()
                            tuiles.update(nouvelles_tuiles)
                            compteurs_joueurs.clear()
                            compteurs_joueurs.update(nouveaux_compteurs)

                if event.type == KEYDOWN and event.key == K_TAB:
                    file_path = self.page_html.generate_html(tuiles)
                    browser = webbrowser.get("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s")
                    browser.open(f"file:///{file_path}")

                if self.menu_active:
                    self.handle_menu_events(event)
                else:
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        if not self.menu_active:
                            self.handle_mini_map_click(mouse_pos)
            if self.menu_active:
                self.show_menu()
            else:
                # self.unit.show_remaining_time()
                self.unit.update_creation_times()
                self.buildings.update_creation_times()
                DISPLAYSURF.fill(BLACK)
                self.tile_map.render(DISPLAYSURF, self.cam_x, self.cam_y)
                self.draw_mini_map(DISPLAYSURF)

                self.unit.update_position()
                current_time = pygame.time.get_ticks()

                for position, data in tuiles.items():
                    if 'unites' in data:
                        position_x, position_y=position
                        self.unit.update_position()
                        self.unit.diplay_unit(position_x, position_y, self.cam_x, self.cam_y, current_time, unit_image)
                if self.unit.position:
                    self.unit.diplay_unit(
                        self.unit.position[0],
                        self.unit.position[1],
                        self.cam_x,
                        self.cam_y,
                        current_time,
                        unit_image
                    )
                self.unit.update_attacks()
                keys = pygame.key.get_pressed()
                self.handle_camera_movement(keys)

                self.Initialisation_compteur.draw_ressources()

                self.Initialisation_compteur.update_compteur()
                fps = int(FPSCLOCK.get_fps())
                fps_text = pygame.font.Font(None, 24).render(f"FPS: {fps}", True, (255, 255, 255))
                DISPLAYSURF.blit(fps_text, (10, 10))
                pygame.display.update()
                pygame.display.flip()

            pygame.display.update()
            FPSCLOCK.tick(60)

