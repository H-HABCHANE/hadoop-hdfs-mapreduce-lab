# Ventes - reducer : somme des prix par ville
# Utilisable aussi comme combiner (la somme est associative).
import sys

courant, total = None, 0.0
for ligne in sys.stdin:
    ville, prix = ligne.rstrip("\n").split("\t")
    if ville != courant:
        if courant is not None:
            print(f"{courant}\t{total:.2f}")
        courant, total = ville, 0.0
    total += float(prix)
if courant is not None:
    print(f"{courant}\t{total:.2f}")
