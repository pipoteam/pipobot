#!/usr/bin/python2
# -*- coding: UTF-8 -*-
import urllib
import os
import sys
sys.path.append("modules/mpd")
from utils import xhtml2text
from BeautifulSoup import BeautifulSoup
#from lib.BotMPD import BotMPD
#try:
#    import config
#except ImportError:
#    raise NameError("MPD config not found, unable to start MPD module")

class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"
urllib._urlopener = AppURLopener()

def query(fields):
#    if fields == "":
#        b = BotMPD(config.HOST, config.PORT, config.PASSWORD)
#        current = b.current()
#        fields = current.partition(".")[2].partition("\n")[0]
    print "fields",fields
    searchpage = "http://www.google.com/custom?hl=fr&domains=http://www.lyricsondemand.com&q=%s&btnG=Rechercher&sitesearch=http://www.lyricsondemand.com"
    query = searchpage%(fields.lower().replace(" ", "+"))
    page = urllib.urlopen(query)
    content = page.read()
    page.close()
    soup = BeautifulSoup(content)
    essai = -1
    success = False
    firstlink = ""
    while essai < 5 and not success:
        try:
            essai += 1
            print essai,soup.findAll("h2")[essai]
            firstlink = soup.findAll("h2")[essai].a["href"]
            success = True
        except: 
            pass
    if firstlink == "":
        return "Dans le cul la balayette"
    link = None
    if firstlink.endswith("html") and not firstlink.endswith("index.html"):
        link = firstlink
    else:
        try:
            artist, title = fields.split("-", 1)
            page = urllib.urlopen(firstlink)
            content = page.read()
            page.close()
            soup = BeautifulSoup(content)
            liste = soup.findAll("span" , {"class": "Highlight"})
            l = [xhtml2text(elt.text.partition("Lyrics")[0]) for elt in liste]
            title = title.lower()
            titles = title.split(" ")
            for elt in liste:
                single = xhtml2text(elt.text.partition("Lyrics")[0])
                found = True
                for name in titles:
                    found = found and (name.lower() in single.lower())
                if found:
                    pagename = elt.a["href"]
                    basename = os.path.split(firstlink)
                    link = basename[0]+"/"+pagename
        except ValueError:
            return "On met artiste - titre pour m'aider un peu vu que je suis nul"
    
    if not link:
        return "Dans le cul la balayette"

    #print link
    page = urllib.urlopen(link)
    content = page.read()
    print "****CONTENT***"
    print content
    page.close()
    lyrics = content.partition('<font size="2" face="Verdana">')[2].split("<script")[0].replace("<BR>", "\n").replace("<br>", "\n")
    #return lyrics
    res1 = xhtml2text(lyrics).strip()
    #post traitement
    post = res1.split("\n")
    middle = len(post) / 2
    col1 = post[0:middle]
    col2 = post[middle:]
    res2 = ""
    colsize = 70
    exception = False
    for i in range(middle):
        try:
            res2 += col1[i] if col1[i] != "\n" else ""
            if len(col1[i]) > colsize:
                exception = True
                break
            res2 += " "*(colsize-len(col1[i]))
            res2 += col2[i] if col2[i] != "\n" else ""
            res2 += "\n"
        except:
            exception = True
            break
    if res2 == "" or exception:
        res2 = res1
    return res2
        

if __name__ == "__main__":
    import sys
    demande = " ".join(sys.argv[1:])
    res = query(demande)
    print res
