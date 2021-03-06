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

import ConfigParser
import datetime
import logging
import optparse
import os
import sys
import threading
import time
from stat import S_ISREG, ST_MODE, ST_MTIME

import pysrt

from fontesLegendas.opensubtitles import OpenSubtitles
from fontesLegendas.thesubdb import TheSubDB


class GetSubCli:
    # TODO: No futuro abilitar essa configuração no arquivo getsubcli.ini
    _fontes = [TheSubDB(), OpenSubtitles()]
    _modoNoturno = 0
    _path = ""
    _pathNoturno = ""
    _pathArquivoLog = ""
    _arquivosBuscarLegendas = []
    _listaThreads = []

    def __init__(self):
        self._parseConfiguracao()
        self.logConfiguracao()

    def logConfiguracao(self):
        if (self._pathArquivoLog != ""):
            logging.basicConfig(format='%(asctime)s %(message)s', filename=self._pathArquivoLog, filemode='a', level=logging.INFO)
        else:
            logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    def _parseConfiguracao(self):
        try:
            parser = ConfigParser.SafeConfigParser()
            parser.read(os.path.dirname(os.path.abspath(__file__)) + "/getsubcli.ini")
            self._modoNoturno = parser.get('GetSubCli', 'modoNoturno')
            try:
                self._pathArquivoLog = parser.get('GetSubCli', 'pathArquivoLog', )
            except ConfigParser.NoOptionError:
                self._pathArquivoLog = ""

            self._path = parser.get('DIR', 'path')
            self._pathNoturno = parser.get('DIR', 'pathNoturno')
        except ConfigParser.NoSectionError as e:
            logging.error("Revisar o seu arquivo de configuração, esta faltando alguma Section nele: " + str(e))
            sys.exit(1)
        except ConfigParser.NoOptionError as e:
            logging.error("Revisar o seu arquivo de configuração, esta faltando uma opção: " + str(e))
            sys.exit(1)
        except:
            logging.error("Erro ao ler os arquivos de configuração. Erro desconhecido: ")
            e = sys.exc_info()[0]
            logging.error(e)
            sys.exit(1)

    # Referencia: https://shoaibmir.wordpress.com/2009/12/14/pid-lock-file-in-python/
    # TODO: Isso não é universal, vai funcionar somente para cliente UNIX
    def lockProc(self):
        if os.access(os.path.expanduser("/tmp/.getsubcli.lock"), os.F_OK):
            pidfile = open(os.path.expanduser("/tmp/.getsubcli.lock"), "r")
            pidfile.seek(0)
            old_pd = pidfile.readline()
            if os.path.exists("/proc/%s" % old_pd):
                logging.error("Programa já em execução.")
                sys.exit(1)
        pidfile = open(os.path.expanduser("/tmp/.getsubcli.lock"), "w")
        pidfile.write("%s" % os.getpid())
        pidfile.close()

    def unLockProc(self):
        os.remove("/tmp/.getsubcli.lock")

    # Referencia: https://gomputor.wordpress.com/2008/09/22/convert-a-file-in-utf-8-or-any-encoding-with-python/
    def converteParaUTF8(self, legenda):

        conteudoLegenda = ""
        conteudoLegendaReconhecido = ""

        # Lista de possivel encodes para a leitura
        encodings = ('utf-8-sig', 'iso-8859-1', 'windows-1253', 'iso-8859-7', 'macgreek')

        # Abrindo o arquivo e lendo ele todo para a variavel conteudoLegenda
        try:
            conteudoLegenda = open(legenda, 'r').read()
        except Exception:
            logging.info("Erro -> Ao abrir o arquivo para converter")

        # Por força bruta vamos tentar descobrir qual é a codificação original do arquivo
        for enc in encodings:
            try:
                conteudoLegendaReconhecido = conteudoLegenda.decode(enc)
                break
            except:
                if enc == encodings[-1]:
                    logging.info("Erro -> Arquivo não é de um formato conhecido para fazer a conversão")
                    sys.exit(1)
                continue

        # Sabendo a condificação original vamos salar ela para UTF-8
        arquivoNovoLegenda = open(legenda, 'w')
        try:
            arquivoNovoLegenda.write(conteudoLegendaReconhecido.encode('utf-8'))
        except Exception, e:
            logging.error(e)
        finally:
            arquivoNovoLegenda.close()


    # Procuro "times" repetidos por força bruta
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

    def limpezaSubtitiles(self,legenda):
        controleLoop = True
        while controleLoop:
            controleLoop = self.removeSubDiplicados(legenda)
        self.converteParaUTF8(legenda)

    def recursivoDiretorio(self, dir):
        if os.path.exists(os.path.join(dir, ".nogetsubcli")):
            return
        for possivelArquivo in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, possivelArquivo)):
                self.recursivoDiretorio(os.path.join(dir, possivelArquivo))
            elif possivelArquivo.endswith(".mkv") | possivelArquivo.endswith(".mp4"):
                self._arquivosBuscarLegendas.append(os.path.join(dir, possivelArquivo))

    #http://stackoverflow.com/questions/168409/how-do-you-get-a-directory-listing-sorted-by-creation-date-in-python/
    def ordernaArquivoBuscarLegendas(self):
        entries = ((os.stat(path), path) for path in self._arquivosBuscarLegendas)
        entries = ((stat[ST_MTIME], path) for stat, path in entries if S_ISREG(stat[ST_MODE]))
        self._arquivosBuscarLegendas = sorted(entries, reverse=True)

    def buscaLegenda(self):
        for cdate, arquivo in self._arquivosBuscarLegendas:
            logging.info("Procurando legendas para o arquivo: " + os.path.basename(arquivo) + " - " + time.ctime(cdate))
            legendaEncontrada = False
            # random.shuffle(self._fontes)
            for f in self._fontes:
                logging.info("  - Procurando em: " + f.getNomeFonte())
                try:
                    achouLegenda = f.procuraLegenda(os.path.join(dir, arquivo))
                except:
                    achouLegenda = False

                if achouLegenda:
                    logging.info("    - Legenda encontrada.")
                    legendaEncontrada = True

                if legendaEncontrada:
                    downloadSucesso = False
                    try:
                        logging.info("    - Fazendo download do arquivo.")
                        f.downloadLegenda(dir, arquivo)
                        logging.info("    - Removendo lixos do arquivo e convertendo para UTF-8, isso pode demorar (Rodando em Backgroud) ..")
                        t = threading.Thread(name=f.getNomeLegenda() , target=self.limpezaSubtitiles, args=(f.getNomeLegenda(),))
                        self._listaThreads.append(t)
                        t.start()
                        downloadSucesso = True
                    finally:
                        if downloadSucesso:
                            break

    def main(self, path):
        logging.info("Iniciando a procura de legendas.")
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

        self.ordernaArquivoBuscarLegendas()
        self.buscaLegenda()

        controleThreads = True
        while controleThreads:
            for th in self._listaThreads:
                if th.is_alive:
                   logging.info("Aguardando o ajuste na legenda %s", th.getName())
                   th.join()
                   self._listaThreads.remove(th)

            if len(self._listaThreads) == 0:
                controleThreads = False


        logging.info("Fim de procura de legendas.")


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-p', dest="path")
    options, remainder = parser.parse_args()

    getsubcli = GetSubCli()
    getsubcli.lockProc()
    getsubcli.main(options.path)
    getsubcli.unLockProc()