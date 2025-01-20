import pickle
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog

class Save_and_load:
    def __init__(self):
        pass

    def sauvegarder_jeu(self, tuiles, compteurs_unites, dossier_sauvegarde="sauvegardes_pickle"):
        try:
            # Crée le dossier si nécessaire
            if not os.path.exists(dossier_sauvegarde):
                os.makedirs(dossier_sauvegarde)

            # Générer un nom de fichier unique basé sur l'heure actuelle
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fichier_sauvegarde = os.path.join(dossier_sauvegarde, f"sauvegarde_{timestamp}.pkl")

            # Préparer les données à sauvegarder
            data = {
                "tuiles": tuiles,
                "compteurs_unites": compteurs_unites
            }

            # Sauvegarder les données en utilisant pickle
            with open(fichier_sauvegarde, 'wb') as fichier:
                pickle.dump(data, fichier)

            print(f"Jeu sauvegardé avec succès dans {fichier_sauvegarde}.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def charger_jeu(self, fichier_sauvegarde):
        try:
            # Charger les données depuis un fichier pickle
            with open(fichier_sauvegarde, 'rb') as fichier:
                data = pickle.load(fichier)

            tuiles = data["tuiles"]
            compteurs_unites = data.get("compteurs_unites", {})  # Récupérer compteurs_unites ou un dict vide

            # Convertir les listes en tuples pour "parent"
            for coord, data in tuiles.items():
                if "batiments" in data:
                    for joueur_bat, batiments in data["batiments"].items():
                        for type_bat, infos in batiments.items():
                            if isinstance(infos.get("parent"), list):
                                infos["parent"] = tuple(infos["parent"])
            print(f"Jeu chargé avec succès depuis {fichier_sauvegarde}.")
            return tuiles, compteurs_unites
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            return None, None

    def choisir_fichier_sauvegarde(self, dossier_sauvegarde="sauvegardes_pickle"):
        try:
            # Crée une fenêtre Tkinter minimale
            root = tk.Tk()
            root.withdraw()  # Masque la fenêtre principale

            # Définit le répertoire par défaut et filtre les fichiers pickle
            fichier = filedialog.askopenfilename(
                initialdir=dossier_sauvegarde,
                title="Choisir une sauvegarde",
                filetypes=(("Fichiers Pickle", "*.pkl"), ("Tous les fichiers", "*.*"))
            )
            return fichier if fichier else None
        except Exception as e:
            print(f"Erreur lors de la sélection : {e}")
            return None
