#! /usr/bin/env python
#-*- coding: utf-8 -*-

class CmdHelp:
    def __init__(self, bot):
        self.bot = bot
        self.command = "help"
        self.desc = "help [commande]\nAffiche la liste des commandes disponible ou l'aide sur une commande précise"
        self.pm_allowed = True
            
    def answer(self, sender, message):
        message = message.lower()
        if message == '':
            l = [] 
            for module in self.bot.commands_sync:
                if hasattr(module, 'genericCmd'):
                    l.append(module.command+" (meta)")
                else:
                    l.append(module.command)
            l.sort()
            return {"text" : self.genString(l), "monospace" : True}
        else:
            for module in self.bot.commands_sync:
                if hasattr(module, 'genericCmd'):
                    if message == module.command:
                        l = module.genericCmd
                        l.sort()
                        return self.genString(l)
                    elif message in module.genericCmd:
                        return module.dico[message]['desc']
                elif module.command == message:
                    return module.desc
            return "Commande non existante"

    def genString(self, l):
        send = 'Votre serviteur peut executer : \n'
        booleen = 0
        i = 0
        while i+2 < len(l):
            cmd1 = l[i]
            cmd2 = l[i+1]
            cmd3 = l[i+2]
            espaces1 = " "*(25 - len(cmd1) - 1)
            espaces2 = " "*(25 - len(cmd2) - 1)
            line = "-%s%s-%s%s-%s\n"%(cmd1, espaces1, cmd2, espaces2, cmd3)
            send += line
            i += 3
        if i < len(l):
            espaces = " "*(25 - len(l[i]) - 1)
            send += "-%s%s"%(l[i], espaces)
        if i +1 < len(l):
            send += "-%s"%(l[i+1])

        return send[:-1]

            
if __name__ == '__main__':
    #Placer ici les tests unitaires
    pass
else:
    from .. import register
    register(__name__, CmdHelp)

