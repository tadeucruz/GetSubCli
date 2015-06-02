#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import datetime
import sys
import optparse

import pysrt

from fontesLegendas.opensubtitles import OpenSubtitles
from fontesLegendas.thesubdb import TheSubDB

_fontes = []

# Referencia: https://shoaibmir.wordpress.com/2009/12/14/pid-lock-file-in-python/
def lockProc():
    if os.access(os.path.expanduser("/tmp/.getsubcli.lock"), os.F_OK):
        pidfile = open(os.path.expanduser("/tmp/.getsubcli.lock"), "r")
        pidfile.seek(0)
        old_pd = pidfile.readline()
        if os.path.exists("/proc/%s" % old_pd):
            print("Programa já em execução.")
            sys.exit(1)
    pidfile = open(os.path.expanduser("/tmp/.getsubcli.lock"), "w")
    pidfile.write("%s" % os.getpid())
    pidfile.close


# Referencia: http://stackoverflow.com/questions/191359/how-to-convert-a-file-to-utf-8-in-python
def converteParaUTF8(legenda):
    sourceEncoding = "iso-8859-1"
    targetEncoding = "utf-8"
    source = open(legenda)
    novo_conteudo = unicode(source.read(), sourceEncoding).encode(targetEncoding)
    source.close()
    target = open(legenda, "w")
    target.write(novo_conteudo)
    target.close()


# Procuro "times" repetidos por forçã bruta
def removeSubDiplicados(legenda):
    subs = pysrt.open(legenda, encoding='iso-8859-1')
    for i in range(len(subs)):
        for x in range(len(subs)):
            if (i != x and subs[i].start == subs[x].start):
                del subs[x]
                subs.save()
                return True
    subs.save(legenda,)
    return False

def recursivoDiretorio(dir):
    for possivelArquivo in os.listdir(dir):
        if os.path.isdir(os.path.join(dir,possivelArquivo)):
            recursivoDiretorio(os.path.join(dir,possivelArquivo))
        elif possivelArquivo.endswith(".mkv") | possivelArquivo.endswith(".mp4"):
            print("Procurando legendas para o arquivo: "+possivelArquivo)
            legendaEncontrada = False
            # Sem muito motivo, basicamente quero tentar random uma fote de legenda
            # random.shuffle(fontes)
            for f in _fontes:
                try:
                    achouLegenda = f.procuraLegenda(os.path.join(dir, possivelArquivo))
                except:
                    achouLegenda = False

                if achouLegenda:
                    print("  - Achamos a legenda de "+possivelArquivo+" em: " + f.getNomeFonte())
                    legendaEncontrada = True

                if legendaEncontrada:
                    downloadSucesso = False
                    try:
                        f.downloadLegenda(dir, possivelArquivo)
                        controleLoop = True
                        while controleLoop:
                            controleLoop = removeSubDiplicados(f.getNomeLegenda())
                        converteParaUTF8(f.getNomeLegenda())
                        downloadSucesso = True
                    finally:
                        if downloadSucesso:
                            break


def main(path):
    # Lista de modulos ativos
    global _fontes
    _fontes = [OpenSubtitles(), TheSubDB()]

    listaPath = ["/mnt/dados/Downloads/", "/mnt/dados/Series"]

    if path:
        recursivoDiretorio(path)
    else:
        dataAtual = datetime.datetime.now()

        # TODO: Tenho certeza que essa não é a melhor maneira, descobrir depois qual seria
        dataControle1 = datetime.datetime.now().replace(hour=00, minute=30, second=0, microsecond=0)
        dataControle2 = datetime.datetime.now().replace(hour=01, minute=30, second=0, microsecond=0)

        if dataAtual >= dataControle1 and dataAtual <= dataControle2:
            recursivoDiretorio("/mnt/dados/Series")
        else:
            recursivoDiretorio("/mnt/dados/Downloads/")

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-p', dest="path")
    options, remainder = parser.parse_args()
    print("Iniciando a procura de legendas.")
    lockProc()
    main(options.path)
    print("Fim de procura de legendas.")