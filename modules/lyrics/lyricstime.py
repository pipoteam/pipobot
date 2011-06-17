#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib
import os
import sys
sys.path.append("modules/mpd")
from BeautifulSoup import BeautifulSoup
from modules.utils import xhtml2text
from lib.BotMPD import BotMPD

try:
    import config
except ImportError:
    raise NameError("MPD config not found, unable to start MPD module")


class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"
urllib._urlopener = AppURLopener()

def query(fields):
    if fields == "":
        b = BotMPD(config.HOST, config.PORT, config.PASSWORD)
        current = b.current()
        fields = current.partition(".")[2].partition("\n")[0]
    #print "fields",fields
    searchpage = "http://www.lyricstime.com/search/?q=%s&t=default"
    query = searchpage%(fields.lower().replace(" ", "+"))
    page = urllib.urlopen(query)
    content = page.read()
    page.close()
    soup = BeautifulSoup(content)
    searchresult = soup.findAll("div",{"id": "searchresult"})
    #print searchresult
    nbresult = int(searchresult[0].findAll("div",{"id":"searchinfo"})[0].text.partition(",")[2].split("Results")[0])
    if nbresult == 0:
        return "Pas de résultat pour la recherche %s : cherche encore !"%(fields)
    else:
        links = searchresult[0].findAll("li")
        link = links[0].a["href"]

    link = "http://www.lyricstime.com%s"%(link)
    #print link
    page = urllib.urlopen(link)
    content = page.read()
    #print "****CONTENT***"
    #print content
    page.close()
    soup = BeautifulSoup(content)
    lyrics = soup.findAll("div",{"id":"songlyrics"})[0]
    #print "********************************************"
    #print str(lyrics)
    #print "********************************************"
    #return lyrics
    res1 = xhtml2text(str(lyrics))
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
    print query("Miley Cyrus - Party in the USA")
