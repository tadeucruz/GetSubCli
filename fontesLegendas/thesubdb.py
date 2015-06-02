#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import os
import urllib2
import codecs

from fontesLegendas import FontesBase


class TheSubDB(FontesBase):
    _linkDownload = ""
    _videoHash = ""
    nomeLegenda = ""

    def getNomeFonte(self):
        return "TheSubDB"

    def __get_hash(self,name):
        readsize = 64 * 1024
        with open(name, 'rb') as f:
            size = os.path.getsize(name)
            data = f.read(readsize)
            f.seek(-readsize, os.SEEK_END)
            data += f.read(readsize)
        return hashlib.md5(data).hexdigest()

    def procuraLegenda(self,arquivo):
        volta = False

        try:
            videoHash = self.__get_hash(arquivo)
            request = urllib2.Request('http://api.thesubdb.com/?action=search&hash=' + str(videoHash))
            request.add_header('User-Agent','SubDB/1.0 (Pyrrot/0.1; http://github.com/jrhames/pyrrot-cli)')
            response = urllib2.urlopen(request)
            if response.code == 200:
                linguaLegendas = response.read()
                if "pt" in linguaLegendas:
                    self._videoHash = videoHash
                    volta = True
        except:
            pass

        return volta

    def downloadLegenda(self, diretorio, arquivo):
        request = urllib2.Request(
            'http://api.thesubdb.com/?action=download&hash=' + str(self._videoHash) + '&language=pt')
        request.add_header('User-Agent','SubDB/1.0 (Pyrrot/0.1; http://github.com/jrhames/pyrrot-cli)')
        response = urllib2.urlopen(request)
        nomeLegenda = os.path.join(diretorio,arquivo)
        nomeLegenda = nomeLegenda[0:len(nomeLegenda)-4]
        with codecs.open(nomeLegenda + ".por.srt", "wb", encoding='utf-8') as local_file:
            local_file.write(response.read())
        self.nomeLegenda = nomeLegenda + ".por.srt"
        
    def getNomeLegenda(self):
        return self.nomeLegenda
