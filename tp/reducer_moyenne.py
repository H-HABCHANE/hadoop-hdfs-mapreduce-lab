# Temperatures - reducer : moyenne par station (somme / nombre)
import sys

courant, somme, nb = None, 0.0, 0
for ligne in sys.stdin:
    station, temp = ligne.rstrip("\n").split("\t")
    if station != courant:
        if courant is not None:
            print(f"{courant}\t{somme / nb:.1f}")
        courant, somme, nb = station, 0.0, 0
    somme += float(temp)
    nb += 1
if courant is not None:
    print(f"{courant}\t{somme / nb:.1f}")
