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

#basico para api
import gzip
import os
import struct
import urllib2
import xmlrpclib

from fontesLegendas import FontesBase


class OpenSubtitles(FontesBase):

    _linkDownload = ""
    nomeLegenda = ""

    def getNomeFonte(self):
        return "OpenSubtitles"

    def __get_hash(self,arquivo):
            longlongformat = '<q'  # little-endian long long
            bytesize = struct.calcsize(longlongformat)

            f = open(arquivo, "rb")

            filesize = os.path.getsize(arquivo)
            hash = filesize

            if filesize < 65536 * 2:
                return "SizeError"

            for x in range(65536 / bytesize):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

            f.seek(max(0, filesize - 65536), 0)
            for x in range(65536 / bytesize):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

            f.close()
            returnedhash = "%016x" % hash
            return returnedhash

    def procuraLegenda(self,arquivo):

        volta = False
        videoTamanho = os.path.getsize(arquivo)
        videoHash = self.__get_hash(arquivo)

        opensubtitles = xmlrpclib.ServerProxy("http://api.opensubtitles.org/xml-rpc")

        saidaLogin = opensubtitles.LogIn("","","pob","OSTestUserAgent")
        token = saidaLogin['token']

        stringProcura = []
        stringProcura.append({'sublanguageid':'pob', 'moviehash':videoHash, 'moviebytesize':str(videoTamanho)})

        listaResultado = opensubtitles.SearchSubtitles(token,stringProcura)
        if listaResultado['data']:
            for i in range(len(listaResultado['data'])):
                nomeLegenda =  listaResultado['data'][i]['SubFileName']
                nomeLegenda = nomeLegenda[0:len(nomeLegenda)-4]
                arquivo = arquivo[0:len(arquivo)-4]
                if nomeLegenda in arquivo:
                    linkDownload = listaResultado['data'][i]['SubDownloadLink']
                    self._linkDownload = linkDownload
                    __videoHash = videoHash
                    volta = True

        opensubtitles.LogOut(token)
        return volta

    def downloadLegenda(self, diretorio, arquivo):
        request = urllib2.Request(self._linkDownload)
        response = urllib2.urlopen(request)

        nomeLegenda = os.path.join(diretorio,arquivo)
        nomeLegenda = nomeLegenda[0:len(nomeLegenda)-4]

        with open("/tmp/algo.gz", "wb") as local_file:
            local_file.write(response.read())

        f = gzip.open("/tmp/algo.gz", "rb")
        file_content = f.read()
        f.close()
        os.remove("/tmp/algo.gz")

        legenda = open(nomeLegenda + ".pt-BR.srt", "w")
        legenda.write(file_content)
        self.nomeLegenda = nomeLegenda + ".pt-BR.srt"
        
    def getNomeLegenda(self):
        return self.nomeLegenda