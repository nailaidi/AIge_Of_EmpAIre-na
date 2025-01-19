from math import sqrt
import math
import pygame
from TileMap import *
from constants import *
from Coordinates import *
from Units import *
import random
import time

class Recolte_ressources:
    def __init__(self):
        self.tile_grass = tile_grass
        self.unit=Unit()

    def trouver_plus_proche_ressource(self, joueur, type_unite, id_unite, ressource):
        position_unite = None
        for position, data in tuiles.items():
            if 'unites' in data and joueur in data['unites']:
                unites_joueur = data['unites'][joueur]
                if type_unite in unites_joueur and id_unite in unites_joueur[type_unite]:
                    position_unite = position
                    break

        if position_unite is None:
            return None  # Unité non trouvée

        # Collecter toutes les positions des ressources 'G' qui sont disponibles (quantité > 0)
        positions_ressources = []
        for position, data in tuiles.items():
            if 'ressources' in data and data['ressources'] == ressource and data.get('quantite', 0) > 0:
                positions_ressources.append(position)
                # Vérifier les bâtiments comme sources de ressources
            elif 'batiments' in data and ressource == 'F':  # Supposons que la ressource 'Farm' désigne les fermes
                for joueur_b, batiments in data['batiments'].items():
                    for type_b, infos_batiment in batiments.items():
                        if type_b == 'F' and infos_batiment.get('quantite',
                                                                0) > 0:  # Vérifier les fermes avec quantité > 0
                            positions_ressources.append(position)
                            break
        def distance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])  # Distance de Manhattan

        plus_proche = None
        distance_minimale = float('inf')
        for pos in positions_ressources:
            dist = distance(position_unite, pos)
            if dist < distance_minimale:
                distance_minimale = dist
                plus_proche = pos

        return plus_proche

    def trouver_plus_proche_batiment(self, joueur, type_unite, id_unite):
        # Trouver la position de l'unité
        position_unite = None
        for position, data in tuiles.items():
            if 'unites' in data and joueur in data['unites']:
                unites_joueur = data['unites'][joueur]
                if type_unite in unites_joueur and id_unite in unites_joueur[type_unite]:
                    position_unite = position
                    break

        if position_unite is None:
            return None  # Unité non trouvée

        # Rechercher les positions des bâtiments appartenant au joueur
        positions_batiments = []
        for position, data in tuiles.items():
            if 'batiments' in data and joueur in data['batiments']:
                for type_b, infos in data['batiments'][joueur].items():
                    if type_b in ['T', 'C']:  # Rechercher uniquement les types 'T' et 'C'
                        positions_batiments.append(position)

        if not positions_batiments:
            return None  # Aucun bâtiment appartenant au joueur trouvé

        # Trouver le bâtiment le plus proche
        def distance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])  # Distance de Manhattan

        plus_proche = None
        distance_minimale = float('inf')
        for pos in positions_batiments:
            dist = distance(position_unite, pos)
            if dist < distance_minimale:
                distance_minimale = dist
                plus_proche = pos

        return plus_proche

    def trouver_tuiles_batiment(self, principal_pos, id_batiment):
        tuiles_batiment = []
        for position, data in tuiles.items():
            if 'batiments' in data:
                for joueur_b, batiments in data['batiments'].items():
                    for type_b, infos_batiment in batiments.items():
                        if infos_batiment.get('id') == id_batiment:
                            # Ajouter les tuiles où le bâtiment est soit le parent, soit principal
                            if infos_batiment.get('parent') == principal_pos or (
                                    infos_batiment.get('principal') and position == principal_pos):
                                tuiles_batiment.append(position)
        return tuiles_batiment

    def recolter_ressource_plus_proche_via_trouver(self, joueur, type_unite, id_unite, posress, recolte_max=20):
        if posress is None:
            return "Aucune ressource disponible à proximité."

        # Trouver la position de l'unité
        position_unite = None
        for position, data in tuiles.items():
            if 'unites' in data and joueur in data['unites']:
                unites_joueur = data['unites'][joueur]
                if type_unite in unites_joueur and id_unite in unites_joueur[type_unite]:
                    position_unite = position
                    break

        if position_unite is None:
            return "Unité introuvable."

        # Accéder aux détails de la ressource ou du bâtiment
        details_ressource = tuiles[posress]

        quantite_disponible = 0
        source = None
        batiment_source = None

        # Déterminer la quantité disponible selon la source (ressource ou bâtiment)
        if 'ressources' in details_ressource and 'quantite' in details_ressource:
            quantite_disponible = details_ressource['quantite']
            source = 'ressource'
        elif 'batiments' in details_ressource:
            for joueur_b, batiments in details_ressource['batiments'].items():
                for type_b, infos_batiment in batiments.items():
                    if type_b == 'F' and 'quantite' in infos_batiment and infos_batiment['quantite'] > 0:
                        quantite_disponible = infos_batiment['quantite']
                        source = 'batiment'
                        batiment_source = infos_batiment
                        id_batiment = infos_batiment['id']
                        principal_pos = infos_batiment.get('parent', posress)
                        break

        # Si aucune ressource valide n'est trouvée
        if quantite_disponible <= 0:
            return "Ressource ou bâtiment épuisé."

        # Calculer la quantité à récolter
        quantite_a_recolter = min(recolte_max, quantite_disponible)

        # Réduire la quantité disponible selon la source
        if source == 'ressource':
            details_ressource['quantite'] -= quantite_a_recolter
            if details_ressource['quantite'] <= 0:
                del tuiles[posress]['ressources']
                del tuiles[posress]['quantite']  # Supprimer si épuisé
        elif source == 'batiment':
            batiment_source['quantite'] -= quantite_a_recolter
            if batiment_source['quantite'] <= 0:
                # Trouver toutes les tuiles liées au bâtiment
                tuiles_batiment = self.trouver_tuiles_batiment(principal_pos, id_batiment)
                print(tuiles_batiment)
                for tuile in tuiles_batiment:
                    if len(tuiles[tuile]) == 1 and 'batiments' in tuiles[tuile]:
                        # Supprimer la tuile entière si elle ne contient que le bâtiment
                        del tuiles[tuile]
                    else:
                        # Sinon, supprimer uniquement les informations liées au bâtiment
                        del tuiles[tuile]['batiments']  # Supprimer toutes les tuiles associées au bâtiment

        # Ajouter la ressource récoltée à la capacité de l'unité
        unite = tuiles[position_unite]['unites'][joueur][type_unite][id_unite]
        print(tuiles)
        unite['capacite'] = str(int(unite['capacite']) + quantite_a_recolter)

        # Exécuter une action si elle est définie
        if action_a_executer:
            action = action_a_executer.pop(0)
            action()

        return f"{quantite_a_recolter} unité(s) de ressource collectée(s)."

    def deposer_ressources(self, quantite, joueur, type_unite, id_unite, ressource):
        position_unite = None
        for position, data in tuiles.items():
            if 'unites' in data and joueur in data['unites']:
                unites_joueur = data['unites'][joueur]
                if type_unite in unites_joueur and id_unite in unites_joueur[type_unite]:
                    position_unite = position
                    break
        compteurs_joueurs[joueur]['ressources'][ressource] += quantite
        unite = tuiles[position_unite]['unites'][joueur][type_unite][id_unite]
        unite['capacite'] = 0