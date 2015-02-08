#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import abc

class FontesBase():

    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def getNomeFonte(self):
        raise NotImplementedError

    @abc.abstractmethod
    def procuraLegenda(self,arquivo):
        raise NotImplementedError
    
    @abc.abstractmethod    
    def downloadLegenda(self,diretorio, arquivo):
        raise NotImplementedError
        
    @abc.abstractmethod
    def getNomeLegenda(self):
        raise NotImplementedError