import json
import ast
from datetime import datetime
from constants import *
import os
import tkinter as tk
from tkinter import filedialog

class Save_and_load :
    def __init__(self):
        pass

    def sauvegarder_jeu(self, tuiles, compteurs_unites, dossier_sauvegarde="sauvegardes"):
        try:
            # Crée le dossier si nécessaire
            if not os.path.exists(dossier_sauvegarde):
                os.makedirs(dossier_sauvegarde)

            # Générer un nom de fichier unique basé sur l'heure actuelle
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fichier_sauvegarde = os.path.join(dossier_sauvegarde, f"sauvegarde_{timestamp}.json")

            # Convertir les clés de tuple en chaînes pour JSON
            tuiles_converties = {str(coord): data for coord, data in tuiles.items()}

            # Préparer les données à sauvegarder
            data = {
                "tuiles": tuiles_converties,
                "compteurs_unites": compteurs_unites
            }

            # Sauvegarder dans un fichier
            with open(fichier_sauvegarde, "w") as fichier:
                json.dump(data, fichier, indent=4)

            print(f"Jeu sauvegardé avec succès dans {fichier_sauvegarde}.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def charger_jeu(self, fichier_sauvegarde):
        try:
            with open(fichier_sauvegarde, "r") as fichier:
                data = json.load(fichier)

            # Charger les tuiles en convertissant les clés de chaînes en tuples
            tuiles_converties = {ast.literal_eval(coord): data for coord, data in data["tuiles"].items()}
            compteurs_unites = data.get("compteurs_unites", {})  # Récupérer compteurs_unites ou un dict vide
            # Convertir les listes en tuples pour "parent"
            for coord, data in tuiles_converties.items():
                if "batiments" in data:
                    for joueur_bat, batiments in data["batiments"].items():
                        for type_bat, infos in batiments.items():
                            if isinstance(infos.get("parent"), list):
                                infos["parent"] = tuple(infos["parent"])
            print(f"Jeu chargé avec succès depuis {fichier_sauvegarde}.")
            return tuiles_converties, compteurs_unites
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            return None, None

    def choisir_fichier_sauvegarde(self,dossier_sauvegarde="sauvegardes"):
        try:
            # Crée une fenêtre Tkinter minimale
            root = tk.Tk()
            root.withdraw()  # Masque la fenêtre principale

            # Définit le répertoire par défaut et filtre les fichiers JSON
            fichier = filedialog.askopenfilename(
                initialdir=dossier_sauvegarde,
                title="Choisir une sauvegarde",
                filetypes=(("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*"))
            )
            return fichier if fichier else None
        except Exception as e:
            print(f"Erreur lors de la sélection : {e}")
            return None
