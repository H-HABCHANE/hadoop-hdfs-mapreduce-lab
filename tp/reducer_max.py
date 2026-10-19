# Temperatures - reducer : maximum par station
# Utilisable aussi comme combiner (le max est associatif).
import sys

courant, maxi = None, None
for ligne in sys.stdin:
    station, temp = ligne.rstrip("\n").split("\t")
    temp = float(temp)
    if station != courant:
        if courant is not None:
            print(f"{courant}\t{maxi}")
        courant, maxi = station, temp
    maxi = max(maxi, temp)
if courant is not None:
    print(f"{courant}\t{maxi}")
