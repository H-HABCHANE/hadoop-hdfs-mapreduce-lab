# Temperatures - combiner : additionne les sommes et les nombres par station
# Meme format en entree et en sortie : (station, somme, nombre).
# Ne divise PAS : il peut donc etre execute 0, 1 ou plusieurs fois.
import sys

courant, somme, nb = None, 0.0, 0
for ligne in sys.stdin:
    station, s, n = ligne.rstrip("\n").split("\t")
    if station != courant:
        if courant is not None:
            print(f"{courant}\t{somme}\t{nb}")
        courant, somme, nb = station, 0.0, 0
    somme += float(s)
    nb += int(n)
if courant is not None:
    print(f"{courant}\t{somme}\t{nb}")
