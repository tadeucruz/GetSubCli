#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from __future__ import print_function
import os
import fontesLegendas
from fontesLegendas.opensubtitles import OpenSubtitles
from fontesLegendas.thesubdb import TheSubDB

#POG
fontes = []

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
                    break


def main():
    global fontes
    fontes = [TheSubDB(), OpenSubtitles()]
    dir = "/mnt/dados/downloads/"
    recursivoDiretorio(dir)
    

if __name__ == '__main__':
    main()