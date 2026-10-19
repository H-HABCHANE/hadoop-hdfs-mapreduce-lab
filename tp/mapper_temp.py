# Temperatures - mapper : emet (station, temperature)
import sys

for ligne in sys.stdin:
    champs = ligne.strip().split(";")
    if len(champs) != 3:
        continue
    station, date, temp = champs
    print(f"{station}\t{temp}")
