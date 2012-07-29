#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
import pprint
import random
import mpd
import utils
import os
import eyeD3

class BotMPD(mpd.MPDClient):
    def __init__(self, host, port, password, datadir=None):
        mpd.MPDClient.__init__(self)
        CON_ID = {'host':host, 'port':port}
        try:
            self.connect(**CON_ID)
            self.password(password)
        except:
            self.disconnect()
            raise NameError("Mauvais hôte ou mot de passe MPD")
        if datadir is None or datadir == "":
            self.datadir = None
        else:
            self.datadir = datadir

    def currentsongf(self):
        song = self.currentsong()
        return utils.format(song)

    def current(self):
        song = self.currentsong()
        playlist = self.status()

        res = self.currentsongf() + "\n"
        res += "[playing] #%s/%s"  % (song["pos"], playlist["playlistlength"])
        if 'time' in playlist.keys():
            current, total = playlist['time'].split(':')
            pcentage = int(100* float(current) / float(total))
            res += "  %s/%s (%s%%)"%(utils.humanize_time(current), utils.humanize_time(total), pcentage)
        return res


    def nextplaylist(self, nb=5):
        nb = int(nb)
        if nb > 15:
            return "Non mais oh, faudrait pas trop exagérer..."
        current = self.currentsong()
        playlist = self.playlistinfo()
        deb = int(current['pos'])
        end = int(self.status()["playlistlength"])
        res = ""
        for i in range(nb):
            song = playlist[(deb + i) % end]
            res += utils.format(song)+"\n"
        return res[:-1]

    def search(self, args):
        l = args.split(' ')
        if len(l) == 2:
            filter = l[0]
            field = l[1]
            req = self.playlistsearch(filter, field)
        else:
            req = self.playlistsearch("Artist", l[0])
            req.extend(self.playlistsearch("Title", l[0]))
        if req == []:
            return "Cherches un peu mieux que ça"
        res = ""
        for elt in req:
            res += "%s\n"%(utils.format(elt))
        return res[0:-1]

    def setnext(self, args):
        try:
            iargs = int(args)
            song = self.currentsong()
            current = song["pos"]
            icurrent = int(current)
            if iargs < icurrent:
                newindex = icurrent
            else:
                newindex = icurrent+1
            self.move(iargs, newindex)
            return self.nextplaylist(3)
        except:
            return "Argument invalide pour setnext..."
    
    def nightmare(self, args=5):
        try: 
            nb = int(args)
            self.update()
            songs = self.lsinfo("nightmare")
            random.shuffle(songs)
            if nb > 15: 
                return "Merilestfou !!!"
            if nb < len(songs):
                selection = songs[0:nb]
            else:
                selection = songs
            playlist = self.status()
            deb = int(playlist["playlistlength"])
            for elt in selection:
                self.add(elt["file"])
            for i in range(deb, deb+nb):
                self.setnext(i)
            send = "/!\\/!\\/!\\/!\\"
            return send
        except ValueError:
            return "Argument invalide pour nightmare..."

    def coffee(self):
        try: 
            songs = self.lsinfo("cafe")
            random.shuffle(songs)
            toadd = songs[0]
            selection = songs[0]
            playlist = self.status()
            deb = int(playlist["playlistlength"])
            self.add(songs[0]["file"])
            self.setnext(deb)
            send = "Coffee en préparation"
            return send
        except ValueError:
            return "Argument invalide pour coffee..."

    def wakeup(self, args=5):
        try: 
            nb = int(args)
            self.update()
            songs = self.lsinfo("wakeup")
            random.shuffle(songs)
            if nb > 15: 
                return "Merilestfou !!!"
            if nb < len(songs):
                selection = songs[0:nb]
            else:
                selection = songs
            playlist = self.status()
            deb = int(playlist["playlistlength"])
            for elt in selection:
                self.add(elt["file"])
            for i in range(deb, deb+nb):
                self.setnext(i)
            send = "ALLER ON SE REVEILLE !!!"
            return send
        except ValueError:
            return "Argument invalide pour nightmare..."

    def goto(self, pos):
        try:
            iargs = int(pos)
            song = self.currentsong()
            current = song["pos"]
            icurrent = int(current)
            self.move(icurrent, iargs)
            return "On s'est déplacé en %s !"%(pos)
        except:
            return "Et un goto foiré, un !"
        
    
    def clean(self):
        nightmare = self.lsinfo("nightmare")
        playlist = self.playlistinfo()
        for elt in nightmare:
            for eltplaylist in playlist:
                if elt["file"] == eltplaylist["file"]:
                    self.deleteid(eltplaylist["id"])
        return "Sauvé...mais pour combien de temps..."

    def connected(self):
        import urllib
        import BeautifulSoup
        import socket
        f = urllib.urlopen("http://admin:pipo@www.sleduc.fr/server-status")
        soup = BeautifulSoup.BeautifulSoup(f.read())
        clients = {}
        res = "Liste des clients connectés sur mpd:\n"
        for tr in soup.findAll("tr"):
            hosts = tr.findAll("td",{"nowrap": "nowrap"})
            for host in hosts:
                if "mpd.sleduc.fr" in host or "mpd.leduc.42" in host:
                    lst = tr.findAll("td")
                    since = utils.humanize_time(lst[5].text)
                    ip = str(lst[10].text)
                    vhost = str(lst[11].text)
                    clients[ip] = (vhost, since)
        for ip,couple in clients.iteritems():
            vhost,since = couple
            try:
                reverse = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                reverse = "Moi y'en a pas savoir résoudre"
            res += "\t- %s (%s)\n\t\tSur %s, depuis %s\n"%(ip, reverse, vhost, since)
        return res[0:-1]

    def settag(self, args):
        if self.datadir is None:
            return "Impossible, datadir non spécifié"
        mess = []
        for couple in args.split('&&'):
            try:
                key, val = couple.strip().split('=')
                key = "setArtist" if key.lower() in ["artist", "artiste", "chanteur", "inteprete", "chose qui chante"] else key
                key = "setTitle" if key.lower() in ["title", "titre", "nom", "denomination du bruit"] else key
                if key in ["setArtist", "setTitle"]:
                    song = self.currentsong()["file"]
                    try:
                        f = os.path.join(self.datadir, song)
                        t = eyeD3.Mp3AudioFile(f).getTag()
                        if t is None:
                            t = eyeD3.Tag()
                            t.link(f)
                            t.header.setVersion(eyeD3.ID3_V2_3)
                        getattr(t, key)(val)
                        t.update()
                        self.update()
                        mess.append("Règle %s en %s" % (key[3:], val))
                    except (eyeD3.tag.InvalidAudioFormatException, IOError):
                        return "Pas mp3 ou permission fail !"
            except ValueError:
                return "Ouiiii, la graMMaire n'est pas respectéee"
        return "\n".join(mess)
