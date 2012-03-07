#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import yaml
import hglib
import mercurial
from lib.modules import SyncModule, answercmd

class CmdHg(SyncModule):
    def __init__(self, bot):
        config = os.path.join(bot.module_path["hg"], "config.yml")
        self.readconf(config)
        desc = """hg : donne le dernier changement sur le repo %s
hg repos : affiche la liste des repos disponibles
hg [repo] : donne le dernier changement du repo [repo]
hg [repo] [rev] : affiche la révision [rev] du repo [repo]""" % (self.defaultrepo)
        SyncModule.__init__(self, 
                            bot, 
                            desc = desc,
                            command = "hg")

    def readconf(self, filename):
        f = open(filename, "r")
        settings = yaml.load(f)
        f.close()
        self.repos = settings["repos"]
        self.defaultrepo = settings["general"]["default"]

    @answercmd(r"^$")
    def answer_default(self, sender, message):
        repo = self.defaultrepo
        return self.get_log(repo, -1)

    @answercmd(r"^(?P<name>\w+)$")
    def answer_repo(self, sender, message):
        repo = message.group("name")
        return self.get_log(repo, -1)

    @answercmd(r"^(?P<name>\w+)\s+(?P<rev>\d+)$")
    def answer_repo_rev(self, sender, message):
        repo = message.group("name")
        rev = message.group("rev")
        return self.get_log(repo, rev)

    def get_log(self, repo, rev):
        if not repo in self.repos:
            return "Le repo %s n'existe pas" % repo
        try:
            return hglib.log(self.repos[repo], int(rev))
        except mercurial.error.RepoError: 
            return "Le répertoire %s associé à %s n'est pas valide !" % (self.repos[repo], repo)
