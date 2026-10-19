# WordCount - mapper : emet (mot, 1) pour chaque mot
import sys

for ligne in sys.stdin:
    for mot in ligne.lower().split():
        print(f"{mot}\t1")
