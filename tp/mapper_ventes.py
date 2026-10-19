# Ventes - mapper : emet (ville, prix) pour chaque vente
import sys

for ligne in sys.stdin:
    champs = ligne.strip().split(";")
    if len(champs) != 4:
        continue  # ligne invalide : on l'ignore
    date, ville, produit, prix = champs
    print(f"{ville}\t{prix}")
