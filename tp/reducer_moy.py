# Temperatures - reducer : additionne les sommes et les nombres, puis divise
import sys

courant, somme, nb = None, 0.0, 0
for ligne in sys.stdin:
    station, s, n = ligne.rstrip("\n").split("\t")
    if station != courant:
        if courant is not None:
            print(f"{courant}\t{somme / nb:.1f}")
        courant, somme, nb = station, 0.0, 0
    somme += float(s)
    nb += int(n)
if courant is not None:
    print(f"{courant}\t{somme / nb:.1f}")
