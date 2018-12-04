from json import dump
from sys import argv
import sys

filename = 'hamlet.txt'
outfile = 'hamlet_10.txt'


with open(filename, 'rb') as fin:
        x = fin.read()

y = x*10


with open(outfile, 'wb') as fout:
    fout.write(y)
