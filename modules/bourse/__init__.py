#! /usr/bin/env python
#-*- coding: utf-8 -*-

import csv
import os
import time 
import sys
from lib.modules import SyncModule, answercmd 

ROOT_URL = 'http://www.banque-france.fr/fr/statistiques/taux/telnomot/'
CACHE_PATH = os.path.abspath(os.path.dirname(sys.argv[0])) + '/modules/bourse'
VALUES = {'CHF':'qs.d.ceurchci.csv', 'USD':'qs.d.ceurusci.csv', 'JPY':'qs.d.ceurjpci.csv', 'CAD':'qs.d.ceurcaci.csv'}
CACHE_LIMIT = 2 * 3600


class CmdBourse(SyncModule):
    def __init__(self, bot):
        desc = u"bourse [valeur [historique]] \n Affiche le taux de conversion d'une valeur boursière.\n"
        desc += u"	Valeurs disponibles: " + ', '.join(VALUES.keys())
        SyncModule(bot, 
                            desc = desc,
                            command = "bourse")

    def answer(self, sender, message) :
	try:
		valeur = message.split(' ')[0]
		histo = int(message.split(' ')[1])
	except:
		valeur = message
		histo = 3

	if not(valeur in VALUES.keys()):
		return self.desc
	else:
		
		#si le fichier est trop vieux, le retelecharger
	        CACHE_FILE = CACHE_PATH + '/' + VALUES[valeur]
		if os.path.isfile(CACHE_FILE) and os.path.getmtime(CACHE_FILE) +CACHE_LIMIT > time.time():
			#cache is up-to-date
			pass
		else:
			if os.path.isfile(CACHE_FILE):
				os.remove(CACHE_FILE)
			os.system('wget ' + ROOT_URL + VALUES[valeur] + ' -O ' + CACHE_FILE )
			os.utime(CACHE_FILE, None)

		#lire et récuppérer les dernieres valeurs:
		f = csv.reader(open(CACHE_FILE, 'r'), delimiter=';')
		buff_date = [''] * histo
		buff_taux = [''] * histo
		header = 7

		for l in f:
			#skip 7-th lines
			if header > 0:
				header-=1
			else:			
				buff_date = buff_date[1:]
				buff_date.append(l[0])
				buff_taux = buff_taux[1:]
				buff_taux.append(l[1])

		output = u"Denières valeurs: \n"
		for i in xrange(histo):
			output += u'%s : %s %s / 1€\n' % (buff_date[i], buff_taux[i], valeur)
		return output
