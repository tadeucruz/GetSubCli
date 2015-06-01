#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

#basico para api
import gzip
import urllib2
import xmlrpclib
import struct
import os

from fontesLegendas import FontesBase


class OpenSubtitles(FontesBase):

    _linkDownload = ""
    __nomeLegenda = ""

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

        legenda = open(nomeLegenda+".srt","wb")
        legenda.write(file_content)
        self.__nomeLegenda = nomeLegenda + "por.srt"
        
    def getNomeLegenda(self):
        return self.__nomeLegenda