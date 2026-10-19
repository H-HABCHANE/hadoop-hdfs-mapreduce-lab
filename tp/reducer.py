# WordCount - reducer : additionne les 1 de chaque mot
# Les lignes arrivent TRIEES par cle : on detecte le changement de mot.
import sys

courant, total = None, 0
for ligne in sys.stdin:
    mot, n = ligne.rstrip("\n").split("\t")
    if mot != courant:
        if courant is not None:
            print(f"{courant}\t{total}")
        courant, total = mot, 0
    total += int(n)
if courant is not None:
    print(f"{courant}\t{total}")
