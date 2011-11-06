#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import yaml
import lib
import mercurial
from lib.modules import SyncModule, answercmd

class CmdHg(SyncModule):
    def __init__(self, bot):
        desc = """hg : donne le dernier changement sur le repo %s
hg repos : affiche la liste des repos disponibles
hg [repo] : donne le dernier changement du repo [repo]
hg [repo] [rev] : affiche la révision [rev] du repo [repo]""" % (self.defaultrepo)
        SyncModule.__init__(bot,
                                    desc = desc,
                                    command = "hg")
        self.readconf("modules/hg/config.yml")

    def readconf(self, filename):
        f = open(filename, "r")
        settings = yaml.load(f)
        f.close()
        self.repos = settings["repos"]
        self.defaultrepo = settings["general"]["default"]

    @answercmd
    def answer(self, sender, message):
        args = message.split(" ")
        #!hg
        if args[0] == "":
            repo = self.defaultrepo
            rev = -1
        #!hg [repo]
        elif len(args) == 1:
            if args[0] == "repos":
                return "Liste des repos : %s et par défaut : %s" % (", ".join(self.repos.keys()), self.defaultrepo)
            repo = args[0]
            rev = -1
        #!hg [repo] [rev]
        elif len(args) == 2:
            repo = args[0]
            rev = args[1]
        else:
            return "Trop d'arguments !"

        if not repo in self.repos:
            return "Le repo %s n'existe pas" % repo
        try:
            return lib.log(self.repos[repo], int(rev))
        except mercurial.error.RepoError: 
            return "Le répertoire %s associé à %s n'est pas valide !" % (self.repos[repo], repo)
