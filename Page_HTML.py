import os
from constants import *


class Page_HTML:
    def __init__(self):
        pass

    def generate_html(self,tuiles):
        # Début du fichier HTML
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Game Snapshot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                h1, h2 {
                    color: #333;
                }
                .tab {
                    display: none;
                }
                .tab-button {
                    background-color: #5d85ab;
                    color: white;
                    padding: 10px 20px;
                    cursor: pointer;
                    border: none;
                    margin-right: 10px;
                    font-size: 16px;
                }
                .tab-button:hover {
                    background-color: #587795;
                }
                .active {
                    background-color: #5d85ab;
                }
                .collapsible {
                    background-color: #777;
                    color: white;
                    cursor: pointer;
                    padding: 10px;
                    width: 100%;
                    border: none;
                    text-align: left;
                    outline: none;
                    font-size: 15px;
                    margin-bottom: 5px;
                }
                .content {
                    padding: 0 18px;
                    display: none;
                    overflow: hidden;
                    background-color: #f1f1f1;
                    margin-bottom: 10px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }
                table, th, td {
                    border: 1px solid #ccc;
                }
                th, td {
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f4f4f4;
                }
            </style>
            <script>
                function showTab(player) {
                    var tabs = document.querySelectorAll('.tab');
                    var buttons = document.querySelectorAll('.tab-button');
                    
                    // Masquer tous les onglets
                    tabs.forEach(tab => tab.style.display = 'none');
                    buttons.forEach(button => button.classList.remove('active'));
        
                    // Afficher l'onglet du joueur sélectionné
                    document.getElementById(player).style.display = 'block';
                    document.querySelector('[data-player="' + player + '"]').classList.add('active');
                }
        
                document.addEventListener("DOMContentLoaded", function() {
                    // Par défaut, on affiche le premier joueur
                    var firstPlayer = document.querySelector('.tab-button');
                    if (firstPlayer) {
                        showTab(firstPlayer.getAttribute('data-player'));
                    }
                    
                    const collapsibles = document.querySelectorAll(".collapsible");
                    collapsibles.forEach(button => {
                        button.addEventListener("click", () => {
                            button.classList.toggle("active");
                            const content = button.nextElementSibling;
                            if (content.style.display === "block") {
                                content.style.display = "none";
                            } else {
                                content.style.display = "block";
                            }
                        });
                    });
                });
            </script>
        </head>
        <body>
            <h1>Game Snapshot</h1>
            <div>
        """

        joueurs = set()
        for coord, data in tuiles.items():
            if "batiments" in data:
                for joueur in data["batiments"]:
                    joueurs.add(joueur)
            if "unites" in data:
                for joueur in data["unites"]:
                    joueurs.add(joueur)

        joueurs_tries = sorted(joueurs, key=lambda x: int(x.split('_')[1]))

        # Création des boutons pour chaque joueur
        for joueur in joueurs_tries:
            html += f'<button class="tab-button" data-player="joueur_{joueur}" onclick="showTab(\'joueur_{joueur}\')">Joueur {joueur}</button>'

        # Création des onglets pour chaque joueur
        for joueur in joueurs:
            html += f'<div id="joueur_{joueur}" class="tab">'
            html += "<h2>Ressources</h2>"
            ressources = compteurs_joueurs[joueur]['ressources']
            html += "<table><tr><th>Bois</th><th>Nourriture</th><th>Or</th><th>Population</th></tr>"
            html += f"<tr><td>{ressources['w']}</td><td>{ressources['f']}</td><td>{ressources['g']}</td><td>{ressources['U']}</td></tr>"
            html += "</table>"

            # Section des unités
            html += "<h2>Unités</h2>"
            unites = compteurs_joueurs[joueur]['unites']
            print(compteurs_joueurs)
            html += "<table><tr><th>Type</th><th>Nombre</th></tr>"
            for type_unite, nombre in unites.items():
                # Conversion des abréviations en noms complets
                if type_unite == 'v':
                    type_unite = "Villageois"
                elif type_unite == 's':
                    type_unite = "Épéiste"
                elif type_unite == 'h':
                    type_unite = "Hallebardier"
                elif type_unite == 'a':
                    type_unite = "Archer"
                html += f"<tr><td>{type_unite}</td><td>{nombre}</td></tr>"
            html += "</table>"

            # Section des bâtiments
            html += "<h2>Bâtiments</h2>"
            batiments_groupes = {}
            for coord, data in tuiles.items():
                if "batiments" in data:
                    for joueur_bat, batiments in data["batiments"].items():
                        if joueur==joueur_bat :
                            for type_bat, infos in batiments.items():
                                parent = infos.get("parent", None)
                                if parent is not None:
                                    if parent not in batiments_groupes:
                                        batiments_groupes[parent] = {
                                            'joueur': joueur_bat,
                                            'type': type_bat,
                                            'id': infos['id'],
                                            'hp': infos['HP'],
                                            'tuiles': []
                                        }
                                    batiments_groupes[parent]['tuiles'].append(coord)

            # Affichage des bâtiments
            html += "<table><tr><th>Joueur</th><th>Type</th><th>ID</th><th>HP</th><th>Tuiles Occupées</th></tr>"
            for parent, infos_bat in batiments_groupes.items():
                tuiles_occupées = ', '.join([f"({x},{y})" for (x, y) in infos_bat['tuiles']])
                html += f"<tr><td>{infos_bat['joueur']}</td><td>{infos_bat['type']}</td><td>{infos_bat['id']}</td><td>{infos_bat['hp']}</td><td>{tuiles_occupées}</td></tr>"
            html += "</table>"

            # Section des unités

            unites_existent = False  # Indicateur pour vérifier la présence d'unités pour le joueur actuel

            # Vérifier s'il y a des unités pour ce joueur
            for coord, data in tuiles.items():
                if "unites" in data and joueur in data["unites"] and data["unites"][joueur]:
                    unites_existent = True
                    break

            if unites_existent:
                html += "<h2>Unités</h2>"
                for coord, data in tuiles.items():
                    if "unites" in data and joueur in data["unites"] and data["unites"][joueur]:
                        html += f"<button class='collapsible'>Coordonnées : {coord}</button>"
                        html += "<div class='content'><table><tr><th>Joueur</th><th>Type</th><th>ID</th><th>HP</th></tr>"
                        for joueur_unite, unites in data["unites"].items():
                            if joueur == joueur_unite:
                                for type_unite, infos in unites.items():
                                    # Remplacement des lettres par des noms complets pour les unités
                                    if type_unite == 'a':
                                        type_unite = "Archer"
                                    elif type_unite == 'v':
                                        type_unite = "Villageois"
                                    elif type_unite == 's':
                                        type_unite = "Épéiste"
                                    elif type_unite == 'c':
                                        type_unite = "Cavalier"
                                    for id_unite, stats in infos.items():
                                        html += f"<tr><td>{joueur_unite}</td><td>{type_unite}</td><td>{id_unite}</td><td>{stats['HP']}</td></tr>"
                        html += "</table></div>"

                # Fermeture de l'onglet du joueur
                html += "</div>"

        # Fin du fichier HTML
        html += """
            </body>
            </html>
            """

        # Écrire dans un fichier
        file_path = os.path.join(os.getcwd(), "game_snapshot.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        return file_path
