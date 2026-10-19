# Genere un fichier de ventes : date;ville;produit;prix
# Usage : python3 generer_ventes.py NB_LIGNES > ventes.csv
import random
import sys

n = int(sys.argv[1]) if len(sys.argv) > 1 else 150000
random.seed(42)  # meme fichier a chaque execution
villes = ["Paris", "Lyon", "Marseille", "Toulouse", "Perpignan",
          "Montpellier", "Bordeaux", "Lille"]
poids = [30, 15, 12, 10, 5, 8, 10, 10]  # Paris vend plus que les autres
produits = ["Vetements", "Musique", "Jouets", "Livres", "Sport"]
for _ in range(n):
    date = f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    ville = random.choices(villes, weights=poids)[0]
    produit = random.choice(produits)
    prix = round(random.uniform(2, 150), 2)
    print(f"{date};{ville};{produit};{prix:.2f}")
