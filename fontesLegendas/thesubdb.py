#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import hashlib
import os
import urllib2

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
        with open(nomeLegenda + ".por.srt", "w") as local_file:
            local_file.write(response.read())
        self.nomeLegenda = nomeLegenda + ".por.srt"
        
    def getNomeLegenda(self):
        return self.nomeLegenda
