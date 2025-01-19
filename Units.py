from math import sqrt
import math
import pygame

from TileMap import *
from constants import *
from Coordinates import *
import random
import time
from Global_image_load import *
from numpy.random import poisson


class Unit:
    def __init__(self):
        self.tile_grass = tile_grass
        self.map_data = map_data  # Dictionnaire global à modifier
        self.compteurs_joueurs = compteurs_joueurs
        self.unit_list = None
        self.current_unit_index = 0

        self.tile_map = TileMap()
        self.coordinates = Coordinates()
        self.id = None  # Identifiant unique pour l'unité

        self.position = None
        self.target_position = None
        self.moving = False
        self.deplacement_termine = False
        self.move_start_time = 0
        self.move_duration = 0
        self.frame_index = 0
        self.direction_index = 0
        self.last_time = pygame.time.get_ticks()
        self.destination = None
        self.moving_unit=None

        self.start_time_offset = 0
        self.attacks_in_progress = []


    def deplacer_unite(self, joueur, type_unite, id_unite, nouvelle_position):
        position_actuelle = None
        for position, data in tuiles.items():
            if 'unites' in data and joueur in data['unites'] and type_unite in data['unites'][joueur]:
                if id_unite in data['unites'][joueur][type_unite]:

                    position_actuelle = position
                    self.position = position
                    print(position_actuelle)
                    break

        if not position_actuelle:
            print(f"Unité {id_unite} non trouvée pour le joueur {joueur}.")
            return

        unite_data = tuiles[position_actuelle]['unites'][joueur][type_unite].pop(id_unite)
        if not tuiles[position_actuelle]['unites'][joueur][type_unite]:
            del tuiles[position_actuelle]['unites'][joueur][type_unite]
        if not tuiles[position_actuelle]['unites'][joueur]:
            del tuiles[position_actuelle]['unites'][joueur]
        if position_actuelle in tuiles:
            if 'unites' in tuiles[position_actuelle]:
                del tuiles[position_actuelle]['unites']


        self.target_position = nouvelle_position
        self.start_moving(nouvelle_position[0], nouvelle_position[1])

        self.moving_unit = {
            "nouvelle_position": nouvelle_position,
            "joueur": joueur,
            "type_unite": type_unite,
            "id_unite": id_unite,
            "unite_data": unite_data
        }

    def start_moving(self, new_x, new_y, duration=2000):
        self.target_position = (new_x, new_y)
        self.move_start_time = pygame.time.get_ticks()
        self.start_time_offset = self.move_start_time
        self.move_duration = duration
        self.moving = True

    def update_position(self):
        if not self.moving:
            return

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time_offset


        if elapsed_time >= self.move_duration:
            self.position = self.target_position
            self.moving = False

            if self.moving_unit:
                nouvelle_position = self.moving_unit["nouvelle_position"]
                joueur = self.moving_unit["joueur"]
                type_unite = self.moving_unit["type_unite"]
                id_unite = self.moving_unit["id_unite"]
                unite_data = self.moving_unit["unite_data"]

                if nouvelle_position not in tuiles:
                    tuiles[nouvelle_position] = {'unites': {}}
                if 'unites' not in tuiles[nouvelle_position]:
                    tuiles[nouvelle_position]['unites'] = {}
                if joueur not in tuiles[nouvelle_position]['unites']:
                    tuiles[nouvelle_position]['unites'][joueur] = {}
                if type_unite not in tuiles[nouvelle_position]['unites'][joueur]:
                    tuiles[nouvelle_position]['unites'][joueur][type_unite] = {}

                tuiles[nouvelle_position]['unites'][joueur][type_unite][id_unite] = unite_data
                self.moving_unit = None
                self.deplacement_termine = True


            if self.deplacement_termine and action_a_executer:
                action = action_a_executer.pop(0)
                action()

        else:

            progress = elapsed_time / self.move_duration
            start_x, start_y = self.position
            target_x, target_y = self.target_position

            new_x = start_x + (target_x - start_x) * progress
            new_y = start_y + (target_y - start_y) * progress
            self.position = (new_x, new_y)





    def animation(self, current_time):  # fonction qui modifie l'indice des frames et le dernier temps du frame
        if current_time - self.last_time > 1000 // 30:  # 1000//30: 30 frames par 1000 millisecondes
            self.last_time = current_time
            self.frame_index = (self.frame_index + 1) % 30

    def frame_coordinates(self, unit_image):
        # calcul des tailles du chaque frame en divisant la taille de l'image principal par le nombre des frames
        frame_width = unit_image.get_width() // 30  # 30 nombre des frames par lignes
        frame_height = unit_image.get_height() // 16  # 16 nombre des frames par colonnes

        # multiplication de l'indice du frame par la taille de chaque frame pour chercher les vrai coordonnees
        frame_x = self.frame_index * frame_width
        frame_y = self.direction_index * frame_height

        return frame_x, frame_y, frame_width, frame_height


    def diplay_unit(self,position_x, position_y, cam_x, cam_y, current_time, unit_image):
        # coordonnées isométrique
        self.update_position()
        iso_x, iso_y = self.coordinates.to_iso(position_x, position_y, cam_x, cam_y,unit_image)

        # appel de la fonction de l'animation
        self.animation(current_time)

        # appel de la fonction frame_coordinates
        frame_x, frame_y, frame_width, frame_height = self.frame_coordinates(unit_image)

        # enlever un frame de l'image principal et l'afficher a la fois
        frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
        unit_frame = unit_image.subsurface(frame_rect)

        DISPLAYSURF.blit(unit_frame, (iso_x, iso_y))



    def conversion(self, x, y):

        # Décalage centré pour le joueur
        centered_col = y - half_size
        centered_row = x - half_size

        # Conversion en coordonnées isométriques
        cart_x = centered_row * tile_grass.width_half
        cart_y = centered_col * tile_grass.height_half

        iso_x = cart_x - cart_y  # Ne pas soustraire cam_x ici
        iso_y = (cart_x + cart_y) / 2  # Ne pas soustraire cam_y ici

        return iso_x, iso_y

    def placer_joueurs_cercle(self, players, rayon, center_x, center_y):
        """Calcule les positions cartésiennes pour `n` joueurs répartis en cercle autour du centre."""
        positions = []
        angle_increment = 360 / players  # Divise le cercle en n parties égales
        for i in range(players):
            angle = angle_increment * i
            cart_x = int(center_x + rayon * math.cos(math.radians(angle)))  # Calcul de la position X
            cart_y = int(center_y + rayon * math.sin(math.radians(angle)))  # Calcul de la position Y
            positions.append((cart_y-2, cart_x-2))  # Ajouter les coordonnées à la liste
        return positions



    #pour del : del tuiles[(60, 110)]['unites']['v'][0]

    def initialisation_compteur(self, position):
        for idx, (joueur, data) in enumerate(compteurs_joueurs.items()):
            x, y = position[idx]  # Position initiale de chaque joueur

            for unite, nombre in data['unites'].items():
                compteurs_unites[unite] = 0

                for i in range(nombre):
                    identifiant_unite = compteurs_unites[unite]
                    compteurs_unites[unite] += 1

                    # Si la tuile (x, y) n'existe pas ou n'est pas un dictionnaire, l'initialiser
                    if (x, y) not in tuiles or not isinstance(tuiles[(x, y)], dict):
                        tuiles[(x, y)] = {}
                        tuiles[(x, y)]['unites'] = {}
                        tuiles[(x, y)]['unites'][joueur] = {}



                    # Vérifier s'il y a un conflit avec les bâtiments ou ressources
                    batiments = tuiles[(x, y)].get('batiments', {})
                    ressources = tuiles[(x, y)].get('ressources', {})

                    if not isinstance(ressources, dict):
                        ressources = {}
                    if not isinstance(batiments, dict):
                        batiments = {}

                    # Vérifier s'il y a des bâtiments ou des ressources sur la tuile
                    tuile_conflit = ('W' in ressources.get(joueur, {}) or
                                     'G' in ressources.get(joueur, {}) or
                                     'T' in batiments.get(joueur, {}) or
                                     'S' in batiments.get(joueur, {}) or
                                     'K' in batiments.get(joueur, {}) or
                                     'H' in batiments.get(joueur, {}) or
                                     'B' in batiments.get(joueur, {}) or
                                     'C' in batiments.get(joueur, {}) or
                                     'F' in batiments.get(joueur, {}) or
                                     'A' in batiments.get(joueur, {}) )

                    # Ajouter l'unité seulement s'il n'y a pas de conflit
                    if not tuile_conflit:
                        if unite not in tuiles[(x, y)]['unites'][joueur]:
                            tuiles[(x, y)]['unites'][joueur][unite] = {}

                        tuiles[(x, y)]['unites'][joueur][unite][identifiant_unite] = {
                            'HP': units_dict[unite]['hp'],  # Récupérer les HP depuis units_images
                            'Status': 'libre',
                            'capacite': '0'
                        }
                    else:
                        # Si conflit, trouver une autre position et réessayer
                        while (x, y) in tuiles and tuile_conflit:
                            x += 1
                            y += 1

                        # Réinitialiser la tuile (x, y) avec les clés nécessaires
                        if (x, y) not in tuiles:
                            tuiles[(x, y)] = {'unites': {}}

                        if joueur not in tuiles[(x, y)]['unites']:
                            tuiles[(x, y)]['unites'][joueur] = {}

                        if unite not in tuiles[(x, y)]['unites'][joueur]:
                            tuiles[(x, y)]['unites'][joueur][unite] = {}

                        tuiles[(x, y)]['unites'][joueur][unite][identifiant_unite] = {
                            'HP': units_dict[unite]['hp'],  # Récupérer les HP depuis units_images
                            'Status': 'libre',
                            'capacite': '0'
                        }
                        #tuiles[(x, y)]['unites'][joueur][unite][identifiant_unite] = {
                        #    'occupé': False  # Récupérer les HP depuis units_images
                        #}

    def attack(self, joueur_a, type_a, id_a, joueur_b, type_b, id_b):
        # Recherche des informations de l'unité attaquante
        position_a = None
        for pos, data in tuiles.items():
            if 'unites' in data and joueur_a in data['unites'] and type_a in data['unites'][joueur_a]:
                if id_a in data['unites'][joueur_a][type_a]:
                    unit_info_a = data['unites'][joueur_a][type_a][id_a]
                    position_a = pos
                    hp_a = unit_info_a['HP']
                    status_a = unit_info_a['Status']
                    break

        # Recherche des informations de l'unité cible
        position_b = None
        for pos, data in tuiles.items():
            if 'unites' in data and joueur_b in data['unites'] and type_b in data['unites'][joueur_b]:
                if id_b in data['unites'][joueur_b][type_b]:
                    unit_info_b = data['unites'][joueur_b][type_b][id_b]
                    position_b = pos
                    hp_b = unit_info_b['HP']
                    status_b = unit_info_b['Status']
                    break

        if not position_a or not position_b:
            print("Erreur : unités introuvables.")
            return

        # Enregistre l'attaque dans les attaques en cours
        self.attacks_in_progress.append({
            "attacker": unit_info_a,
            "attacker_position": position_a,
            "target_position": position_b,
            "target_hp": hp_b,
            "target": {
                "joueur": joueur_b,
                "type": type_b,
                "id": id_b
            },
            "attack_power": units_dict[type_a]['attaque'],
            "range": units_dict[type_a].get('range', 1),
            "next_attack_time": pygame.time.get_ticks() + 1000,  # Première attaque après 1 seconde
            "is_building_attack": False  # Pour différencier unité vs bâtiment
        })

    def attack_building(self, joueur_a, type_a, id_a, joueur_b, type_b, id_b):
        # Initialisation des positions
        position_a = None

        # Recherche des caractéristiques de l'unité A
        for pos, data in tuiles.items():
            if 'unites' in data and joueur_a in data['unites'] and type_a in data['unites'][joueur_a]:
                if id_a in data['unites'][joueur_a][type_a]:
                    unit_info_a = data['unites'][joueur_a][type_a][id_a]
                    position_a = pos
                    hp_a = unit_info_a['HP']
                    status_a = unit_info_a['Status']
                    capacite_a = unit_info_a.get('capacite', 0)
                    break

        # Vérification que l'unité A a bien été trouvée
        if position_a is None:
            print(f"Erreur : unité {type_a} avec ID {id_a} du joueur {joueur_a} introuvable.")
            return

        # Recherche des caractéristiques dans `units_dict` pour unité A
        unit_data_a = units_dict[type_a]
        lettre_a = type_a
        attaque_a = unit_data_a['attaque']
        range_a = unit_data_a.get('range', 1)

        # Recherche du bâtiment B
        building_tiles = []
        building_hp = None

        for pos, data in tuiles.items():
            if 'batiments' in data and joueur_b in data['batiments'] and type_b in data['batiments'][joueur_b]:
                if data['batiments'][joueur_b][type_b]['id'] == id_b:
                    building_info_b = data['batiments'][joueur_b][type_b]
                    parent_b = building_info_b['parent']
                    building_hp = building_info_b['HP']

                    # Collecte toutes les tuiles appartenant au bâtiment (ayant le même parent)
                    if building_info_b['parent'] == parent_b:
                        building_tiles.append((pos, building_info_b))

        if not building_tiles:
            print(f"Erreur : bâtiment {type_b} avec ID {id_b} du joueur {joueur_b} introuvable.")
            return

        # Enregistre l'attaque dans les tâches en cours
        self.attacks_in_progress.append({
            "attacker": unit_info_a,
            "attacker_position": position_a,
            "target_hp": building_hp,
            "target_position": parent_b,
            "building_tiles": building_tiles,
            "target": {
                "joueur": joueur_b,
                "type": type_b,
                "id": id_b
            },
            "attack_power": attaque_a,
            "range": range_a,
            "is_building_attack": True,
            "next_attack_time": pygame.time.get_ticks() + 1000
        })

    def update_attacks(self):
        current_time = pygame.time.get_ticks()
        completed_attacks = []

        for attack in self.attacks_in_progress:
            if current_time >= attack["next_attack_time"]:
                attacker = attack["attacker"]
                attack_power = attack["attack_power"]
                target_hp = attack["target_hp"]
                range_a = attack["range"]
                attacker_position = attack["attacker_position"]
                target_position = attack["target_position"]

                if attack["is_building_attack"]:
                    # Gestion des attaques contre des bâtiments
                    building_tiles = attack["building_tiles"]
                    target_position = attack["target_position"]

                    distance = abs(attacker_position[0] - target_position[0]) + abs(
                        attacker_position[1] - target_position[1])

                    if distance <= range_a:
                        attack["target_hp"] -= attack_power
                        print(
                            f"L'unité inflige {attack_power} dégâts au bâtiment. HP restant : {max(attack['target_hp'], 0)}")
                        attack["next_attack_time"] = current_time + 1000

                        if attack["target_hp"] <= 0:
                            print(f"Le bâtiment est détruit !")
                            completed_attacks.append(attack)

                            for pos, building_part in building_tiles:
                                if "ressources" not in tuiles[pos] and "unites" not in tuiles[pos]:
                                    # Si la tuile ne contient ni "ressources" ni "unites", supprimer la tuile complètement
                                    del tuiles[pos]
                                else:
                                    # Sinon, on supprime les bâtiments présents dans la tuile
                                    if len(tuiles[pos]) == 1:
                                        del tuiles[pos]["batiments"]
                                    else:
                                        del tuiles[pos]["batiments"][building_part['joueur']][building_part['type']]
                            print(tuiles)
                            joueur_b = attack["target"]["joueur"]
                            type_b = attack["target"]["type"]
                            id_b = attack["target"]["id"]
                            if joueur_b in compteurs_joueurs:
                                if type_b in compteurs_joueurs[joueur_b]['batiments'] and \
                                        compteurs_joueurs[joueur_b]['batiments'][type_b] > 0:
                                    compteurs_joueurs[joueur_b]['batiments'][type_b] -= 1

                else:
                    # Gestion des attaques contre des unités
                    distance = abs(attacker_position[0] - target_position[0]) + abs(
                        attacker_position[1] - target_position[1])

                    if distance <= range_a:
                        attack["target_hp"] -= attack_power
                        print(
                            f"L'unité inflige {attack_power} dégâts à l'unité. HP restant : {max(attack['target_hp'], 0)}")
                        attack["next_attack_time"] = current_time + 1000

                        if attack["target_hp"] <= 0:
                            print(f"L'unité est détruite !")
                            completed_attacks.append(attack)

                            # Suppression de l'unité de `tuiles`
                            joueur_b = attack["target"]["joueur"]
                            type_b = attack["target"]["type"]
                            id_b = attack["target"]["id"]
                            del tuiles[target_position]['unites'][joueur_b][type_b][id_b]
                            if joueur_b in compteurs_joueurs:
                                if type_b in compteurs_joueurs[joueur_b]['unites'] and \
                                        compteurs_joueurs[joueur_b]['unites'][type_b] > 0:
                                    compteurs_joueurs[joueur_b]['unites'][type_b] -= 1


        for attack in completed_attacks:
            self.attacks_in_progress.remove(attack)

    def decrementer_hp_unite(self):
        # Vérifier que les tuiles existent et contiennent des unités
        for (x, y), data in tuiles.items():
            if isinstance(data, dict) and 'unites' in data:  # Vérifie si la tuile contient des unités
                unites = data['unites']

                # Parcourir les joueurs
                for joueur, joueur_unites in unites.items():
                    # Parcourir les types d'unités
                    for unite, instances in joueur_unites.items():
                        # Prendre uniquement la première unité trouvée
                        for identifiant, stats in instances.items():
                            if 'HP' in stats:
                                stats['HP'] -= 4  # Réduire les HP de 4

                                # Si l'unité est morte, la supprimer
                                if stats['HP'] <= 0:
                                    stats['HP'] = 0
                                    del tuiles[(x, y)]['unites'][joueur][unite][identifiant]
                                    if joueur in compteurs_joueurs:
                                        if unite in compteurs_joueurs[joueur]['unites'] and \
                                                compteurs_joueurs[joueur]['unites'][unite] > 0:
                                            compteurs_joueurs[joueur]['unites'][unite] -= 1


                                    # Supprimer les structures vides
                                    if not tuiles[(x, y)]['unites'][joueur][unite]:
                                        del tuiles[(x, y)]['unites'][joueur][unite]
                                    if not tuiles[(x, y)]['unites'][joueur]:
                                        del tuiles[(x, y)]['unites'][joueur]
                                    if not tuiles[(x, y)]['unites']:
                                        del tuiles[(x, y)]['unites']
                                return

    def creation_unite(self, unit_type, player):

        # Définir le type de bâtiment nécessaire pour chaque unité
        required_buildings = {"v": "T", "a": "A", "h": "H", "s": "S"}
        building_type = required_buildings.get(unit_type)

        required_cost = units_dict[unit_type]['cout']
        if (compteurs_joueurs[player]["ressources"]['W'] >= required_cost['W']
                and compteurs_joueurs[player]["ressources"]['G'] >= required_cost['G']
                and compteurs_joueurs[player]["ressources"]['f'] >= required_cost['f']):
            if not building_type:
                return
            if compteurs_joueurs[player]['ressources']['U'] < compteurs_joueurs[player]['ressources']['max_pop']:

                # Rechercher les bâtiments valides pour le joueur
                for (x, y), tile in tuiles.items():
                    if "batiments" in tile and player in tile["batiments"]:
                        if building_type in tile["batiments"][player]:
                            # Ajouter à la file d'attente de ce bâtiment
                            compteurs_joueurs[player]["ressources"]['W'] -= required_cost['W']
                            compteurs_joueurs[player]["ressources"]['f'] -= required_cost['f']
                            compteurs_joueurs[player]["ressources"]['G'] -= required_cost['G']
                            if player in compteurs_joueurs:
                                if unit_type in compteurs_joueurs[player]['unites']:
                                    compteurs_joueurs[player]['unites'][unit_type] += 1
                                    compteurs_joueurs[player]['ressources']['U'] += 1
                                    print("incrémentation compteur", compteurs_joueurs[player]['ressources']['U'])
                            self.add_unit_to_queue(unit_type, player, (x, y))

                            return
            else :
                print("nombre max d'unité atteint")
            print("pas assez de ressources")

    def is_tile_empty(self, position):
        tile = tuiles.get(position, {})
        return "batiments" not in tile and "ressources" not in tile

    def add_unit_to_tile(self, unit_type, player, position):

        if position not in tuiles:
            tuiles[position] = {}

        if "unites" not in tuiles[position]:
            tuiles[position]["unites"] = {}

        if player not in tuiles[position]["unites"]:
            tuiles[position]["unites"][player] = {}

        if unit_type not in tuiles[position]["unites"][player]:
            tuiles[position]["unites"][player][unit_type] = {}

        existing_units = tuiles[position]["unites"][player][unit_type]
        new_unit_id = max(existing_units.keys(), default=-1) + 1

        tuiles[position]["unites"][player][unit_type][new_unit_id] = {"HP": units_dict[unit_type]['hp']}




    def add_unit_to_queue(self, unit_type, player, building_position):
        temps_creation = units_dict[unit_type]["temps_entrainement"]
        creation_time = temps_creation

        tile = tuiles.get(building_position, {})
        if "unit_creation_queue" not in tile:
            tile["unit_creation_queue"] = []

        tile["unit_creation_queue"].append({
            "type": unit_type,
            "player": player,
            "time_started": None,  # Enregistrez l'heure actuelle
            "creation_time": creation_time
        })



    def get_building_type_from_position(self, position):
        """Récupère le type de bâtiment et l'origine à partir d'une position donnée."""
        tile = tuiles.get(position, {})  # Récupérer la tuile à partir de la position

        # Vérifier si la tuile contient des bâtiments
        if "batiments" in tile:
            for player, buildings in tile["batiments"].items():
                for building_type, building_data in buildings.items():
                    # Vérifier que le bâtiment a une clé "parent" et récupérer l'origine
                    if "parent" in building_data:
                        origin = building_data["parent"]  # Récupérer la position du bâtiment principal
                        origin_tile = tuiles.get(origin, {})  # Récupérer la tuile de l'origine (bâtiment principal)

                        # Si l'origine est valide, on peut obtenir le type de bâtiment
                        if origin_tile and "batiments" in origin_tile:
                            for player_origin, buildings_origin in origin_tile["batiments"].items():
                                for origin_building_type, origin_building_data in buildings_origin.items():
                                    # Retourner le type de bâtiment trouvé à l'origine
                                    return origin_building_type, origin
                        else:
                            print(f"Aucune origine valide trouvée pour la tuile à {origin}.")
        return None, None

    def update_creation_times(self):
        current_time = time.time()  # Obtenez le temps actuel
        for position, tile in list(tuiles.items()):  # Utilisez list() pour éviter des erreurs lors de modifications
            if "unit_creation_queue" in tile:
                queue = tile["unit_creation_queue"]

                # Traiter uniquement la première unité dans la file d'attente
                if queue:
                    first_unit = queue[0]

                    # Démarrer la création si elle n'a pas encore commencé
                    if first_unit.get("time_started") is None:
                        first_unit["time_started"] = current_time
                        print(
                            f"Début de la création de l'unité {first_unit['type']} pour {first_unit['player']} à {position}.")

                    # Calculer le temps écoulé pour la première unité
                    elapsed_time = current_time - first_unit["time_started"]

                    # Si la première unité est terminée
                    if elapsed_time >= first_unit["creation_time"]:
                        # Obtenir le type de bâtiment et sa taille
                        building_type, origin = self.get_building_type_from_position(position)
                        if not building_type:
                            print(f"Aucun type de bâtiment trouvé à la position {position}.")
                            continue
                        building_size = builds_dict.get(building_type, {}).get('taille', 1)

                        # Calculer toutes les positions occupées par le bâtiment
                        building_positions = [
                            (origin[0] + dx, origin[1] + dy)
                            for dx in range(building_size)
                            for dy in range(building_size)
                        ]

                        # Liste des positions adjacentes par priorité
                        adjacent_positions = set()

                        # Ajouter toutes les cases adjacentes directement autour du bâtiment
                        for building_pos in building_positions:
                            x, y = building_pos
                            # Positions adjacentes immédiates
                            for adj_pos in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
                                if adj_pos not in building_positions:  # Ignorer les cases du bâtiment
                                    adjacent_positions.add(adj_pos)

                        # Passer à un rayon croissant uniquement si nécessaire
                        radius = 1
                        while True:
                            # Ajouter des positions pour le rayon actuel
                            if radius > 1:
                                for building_pos in building_positions:
                                    for dx in range(-radius, radius + 1):
                                        for dy in range(-radius, radius + 1):
                                            adj_pos = (building_pos[0] + dx, building_pos[1] + dy)
                                            if adj_pos not in building_positions:
                                                adjacent_positions.add(adj_pos)

                            # Rechercher une position vide
                            for adj_pos in sorted(adjacent_positions):  # Tri optionnel pour un placement plus stable
                                if self.is_tile_empty(adj_pos):
                                    self.add_unit_to_tile(first_unit["type"], first_unit["player"], adj_pos)
                                    print(f"Unité {first_unit['type']} placée pour {first_unit['player']} à {adj_pos}.")
                                    queue.pop(0)  # Retirer l'unité de la file d'attente
                                    break
                            else:
                                # Si aucune tuile vide n'est trouvée dans ce rayon, augmenter le rayon
                                radius += 1
                                print(f"Aucune tuile vide trouvée à un rayon de {radius - 1}, augmentation à {radius}.")
                                continue

                            # Si une unité a été placée, arrêter la recherche
                            break

                        # Supprimer la clé "unit_creation_queue" si la liste est vide
                        if not queue:
                            del tile["unit_creation_queue"]
                            print(f"File d'attente vidée et supprimée pour {position}.")

    def show_remaining_time(self):
        current_time = time.time()
        for position, tile in tuiles.items():
            if "unit_creation_queue" in tile and tile["unit_creation_queue"]:
                first_unit = tile["unit_creation_queue"][0]
                if first_unit.get("time_started") is not None:
                    remaining_time = first_unit["creation_time"] - (current_time - first_unit["time_started"])
                    if remaining_time > 0:
                        print(
                            f"Unité {first_unit['type']} en cours pour {first_unit['player']} à {position}. Temps restant : {int(remaining_time)} sec")





class Villager(Unit):
    def __init__(self, image, lettre='v', cout={'Gold': 0, 'Food': 50, 'Wood': 0}, hp=25, temps_entrainement= 25,attaque=2, vitesse=0.8):
        super().__init__(image, lettre, cout, hp, temps_entrainement, attaque, vitesse)


class Swordman(Unit):
    def __init__(self, image, lettre='s', cout={'Gold': 20, 'Food': 50, 'Wood': 0}, hp=40, temps_entrainement= 20,attaque=4, vitesse=0.9):
        super().__init__(image, lettre, cout, hp, temps_entrainement, attaque, vitesse)


class Horseman(Unit):
    def __init__(self,image, lettre='h', cout={'Gold': 20, 'Food': 80, 'Wood': 0}, hp=45, temps_entrainement= 30,attaque=4, vitesse=1.2):
        super().__init__(image, lettre, cout, hp, temps_entrainement, attaque, vitesse)


class Archer(Unit):
    def __init__(self, image, lettre='a', cout={'Gold': 45, 'Food': 0, 'Wood': 25}, hp=30, temps_entrainement= 35, attaque=4, vitesse=1):
        super().__init__(image, lettre, cout, hp, temps_entrainement, attaque, vitesse)