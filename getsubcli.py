#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from __future__ import print_function
import os
import datetime

from fontesLegendas.opensubtitles import OpenSubtitles
from fontesLegendas.thesubdb import TheSubDB




#Removendo times repetidos
import pysrt

#POG
fontes = []

# Procuro "times" repetidos por for�� bruta
def removeSubDiplicados(legendas):
    subs = pysrt.open(legendas, encoding='iso-8859-1')
    for i in range(len(subs)):
        for x in range(len(subs)):
            if (i != x and subs[i].start == subs[x].start):
                del subs[x]
                subs.save()
                return True
    return False

def recursivoDiretorio(dir):
    for possivelArquivo in os.listdir(dir):
        if os.path.isdir(os.path.join(dir,possivelArquivo)):
            recursivoDiretorio(os.path.join(dir,possivelArquivo))
        elif possivelArquivo.endswith(".mkv") | possivelArquivo.endswith(".mp4"):
            print("Procurando legendas para o arquivo: "+possivelArquivo)
            legendaEncontrada = False
            for f in fontes:
                if f.procuraLegenda(os.path.join(dir, possivelArquivo)):
                    print("  - Achamos a legenda de "+possivelArquivo+" em: " + f.getNomeFonte())
                    legendaEncontrada = True
                if legendaEncontrada:
                    f.downloadLegenda(dir,possivelArquivo)
                    controleLoop=True
                    while controleLoop:
                        controleLoop = removeSubDiplicados(f.getNomeLegenda())
                    break


def main():
    global fontes
    fontes = [TheSubDB(), OpenSubtitles()]
    dataAtual = datetime.datetime.now()

    # TODO: Tenho certeza que essa n�o � a melhor maneira, descobrir depois qual seria
    dataControle1 = datetime.datetime.now().replace(hour=00, minute=30, second=0, microsecond=0)
    dataControle2 = datetime.datetime.now().replace(hour=01, minute=30, second=0, microsecond=0)

    if dataAtual >= dataControle1 and dataAtual <= dataControle2:
        recursivoDiretorio("/mnt/dados/Series")
    else:
        recursivoDiretorio("/mnt/dados/Downloads/")

if __name__ == '__main__':
    main()