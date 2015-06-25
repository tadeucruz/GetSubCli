#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
import os
import datetime
import sys
import optparse
import ConfigParser
import random

import pysrt

from fontesLegendas.opensubtitles import OpenSubtitles
from fontesLegendas.thesubdb import TheSubDB


class GetSubCli:
    # TODO: No futuro abilitar essa configuração no arquivo getsubcli.ini
    _fontes = [OpenSubtitles(), TheSubDB()]
    _modoNoturno = 0
    _path = ""
    _pathNoturno = ""

    def __init__(self):
        self._parseConfiguracao()

    def _parseConfiguracao(self):
        try:
            parser = ConfigParser.SafeConfigParser()
            parser.read(os.path.dirname(os.path.abspath(__file__)) + "/getsubcli.ini")
            self._modoNoturno = parser.get('GetSubCli', 'modoNoturno')
            self._path = parser.get('DIR', 'path')
            self._pathNoturno = parser.get('DIR', 'pathNoturno')
        except ConfigParser.NoSectionError as e:
            print("Revisar o seu arquivo de configuração, esta faltando alguma Section nele: " + str(e))
            sys.exit(1)
        except ConfigParser.NoOptionError as e:
            print("Revisar o seu arquivo de configuração, esta faltando uma opção: " + str(e))
            sys.exit(1)
        except:
            print("Erro ao ler os arquivos de configuração. Erro desconhecido: ")
            e = sys.exc_info()[0]
            print(e)
            sys.exit(1)

    # Referencia: https://shoaibmir.wordpress.com/2009/12/14/pid-lock-file-in-python/
    # TODO: Isso não é universal, vai funcionar somente para cliente UNIX
    def lockProc(self):
        if os.access(os.path.expanduser("/tmp/.getsubcli.lock"), os.F_OK):
            pidfile = open(os.path.expanduser("/tmp/.getsubcli.lock"), "r")
            pidfile.seek(0)
            old_pd = pidfile.readline()
            if os.path.exists("/proc/%s" % old_pd):
                print("Programa já em execução.")
                sys.exit(1)
        pidfile = open(os.path.expanduser("/tmp/.getsubcli.lock"), "w")
        pidfile.write("%s" % os.getpid())
        pidfile.close()

    def unLockProc(self):
        os.remove("/tmp/.getsubcli.lock")

    # Referencia: http://stackoverflow.com/questions/191359/how-to-convert-a-file-to-utf-8-in-python
    def converteParaUTF8(self, legenda):
        sourceEncoding = "iso-8859-1"
        targetEncoding = "utf-8"
        source = open(legenda)
        novo_conteudo = unicode(source.read(), sourceEncoding).encode(targetEncoding)
        source.close()
        target = open(legenda, "w")
        target.write(novo_conteudo)
        target.close()

    # Procuro "times" repetidos por forçã bruta
    def removeSubDiplicados(self, legenda):
        subs = pysrt.open(legenda, encoding='iso-8859-1')
        for i in range(len(subs)):
            for x in range(len(subs)):
                if (i != x and subs[i].start == subs[x].start):
                    del subs[x]
                    subs.save()
                    return True
        subs.save(legenda, )
        return False

    def recursivoDiretorio(self, dir):
        for possivelArquivo in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, possivelArquivo)):
                self.recursivoDiretorio(os.path.join(dir, possivelArquivo))
            elif possivelArquivo.endswith(".mkv") | possivelArquivo.endswith(".mp4"):
                print("Procurando legendas para o arquivo: " + possivelArquivo)
                legendaEncontrada = False
                random.shuffle(self._fontes)
                for f in self._fontes:
                    try:
                        achouLegenda = f.procuraLegenda(os.path.join(dir, possivelArquivo))
                    except:
                        achouLegenda = False

                    if achouLegenda:
                        print("  - Achamos a legenda de " + possivelArquivo + " em: " + f.getNomeFonte())
                        legendaEncontrada = True

                    if legendaEncontrada:
                        downloadSucesso = False
                        try:
                            f.downloadLegenda(dir, possivelArquivo)
                            controleLoop = True
                            while controleLoop:
                                controleLoop = self.removeSubDiplicados(f.getNomeLegenda())
                            self.converteParaUTF8(f.getNomeLegenda())
                            downloadSucesso = True
                        finally:
                            if downloadSucesso:
                                break

    def main(self, path):

        if path:
            self.recursivoDiretorio(path)
        else:
            dataAtual = datetime.datetime.now()

            # TODO: Tenho certeza que essa não é a melhor maneira, descobrir depois qual seria
            dataControle1 = datetime.datetime.now().replace(hour=00, minute=30, second=0, microsecond=0)
            dataControle2 = datetime.datetime.now().replace(hour=01, minute=30, second=0, microsecond=0)

            if dataAtual >= dataControle1 and dataAtual <= dataControle2:
                self.recursivoDiretorio(self._pathNoturno)
            else:
                self.recursivoDiretorio(self._path)

if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('-p', dest="path")
    options, remainder = parser.parse_args()

    getsubcli = GetSubCli()

    print("Iniciando a procura de legendas.")
    getsubcli.lockProc()

    # try:
    getsubcli.main(options.path)
    getsubcli.unLockProc()
    # except  :
    #    print("Algo de errado, um erro que não foi tratado")
    #    print(sys.exc_info()[0])

    print("Fim de procura de legendas.")