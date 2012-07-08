#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

class Pendu(object):
    def __init__(self, word):
        self.setword(word)

    def setword(self, word):
        self._word = word
        self.played = ["_"]*len(word)
        self.letters = set()
        self.okletters = set()
        self.maxanswers = 6

    def getword(self):
        return self._word
    
    word = property(getword, setword)

    def playedtostr(self):
        return "Lettres jouées: " + ", ".join(self.letters) + ", ".join(self.okletters)

    def propose(self, letter):
        res = ""
        if letter in self.letters:
            res = "Lettre déjà proposée"
        else:
            if len(self.letters) == self.maxanswers -1:
                rep = "%s fails : c'est fini !!!!"%(len(self.letters))
                rep += " Tu devais trouver %s"%(self.word)
                return rep
            if letter in self.word:
                i = -1
                for l in self.word:
                    i += 1
                    if l == letter:
                        self.played[i] = self.word[i]
                        self.okletters.add(letter)
                res = "Bien vu !"
                if self.solved():
                    res += "\nEt oui, le mot à trouver était bien %s !"%(self.word)
                else:
                    res += " Mot actuel: %s"%("".join(self.played))
            else:
                self.letters.add(letter)
                res = "Cherches encore !"
        return res

    def solved(self):
        return not ("_" in self.played)

if __name__ == "__main__":
    g = Pendu("pipo")
    print g.played
    print g.propose("p")
    print g.playedtostr()
    print g.solved()
    print g.propose("r")
    print g.playedtostr()
    print g.solved()
    print g.propose("i")
    print g.playedtostr()
    print g.solved()
    print g.propose("o")
