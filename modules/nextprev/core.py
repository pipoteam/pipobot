#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import re
import urllib
import datetime
import urllib2
import gzip
from StringIO import StringIO

import urllib

class AppURLopener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return ('', '')

    version = "Mozilla/5.0 (X11; U; Linux; fr-fr) AppleWebKit/531+ (KHTML, like Gecko) Safari/531.2+ Midori/0.2"
urllib._urlopener = AppURLopener()

alias = {
            'sgu': 'stargate-universe',
            'tbbt': 'the-big-bang-theory',
            'itcrowd': 'the-it-crowd',
            'southpark': 'south-park',
            'fma': 'fullmetal-alchemist-brotherhood',
            'himym': 'how-i-met-your-mother',
            'to': 'the-office-us',
            'simpsons': 'the-simpsons',
            'seeker': 'legend-of-the-seeker',
            'sp': 'south-park',
            'clonewars': 'star-wars-the-clone-wars'
        }



def getdata(message, isnext):
    res = ""
    precornext = "suivant" if isnext else "précédent"
    if isnext:
        reep = re.compile('Next episode: </strong>[^<]*<span class="a2"><a href="http://[^>]*" target="_blank" rel="nofollow">([^<]*)', re.M)
        redate = re.compile('Date:</td>[^<td]*<td nowrap class="nextEpInfo" width="300">([^</]*)', re.M)
        reseason = re.compile('Season:</td>[^<td]*<td class="nextEpInfo"  width="300">([^</]*)', re.M)
        renum = re.compile('Number:</td>[^<td]*<td class="nextEpInfo"  width="300">([^</]*)', re.M)
        reparachute = re.compile('However, our last information about it is: <br><br><b>([^<]*)', re.M)
    else:
        reep = re.compile('Previous episode: </strong>[^<]*<span class="a2"><a href="http://[^>]*" target="_blank" rel="nofollow">([^<]*)', re.M)
        redate = re.compile('Date:</td>[^<td]*<td nowrap class="nextEpInfo"  width="300">([^</]*)', re.M)
        reseason = re.compile('Season:</td>[^<td]*<td class="nextEpInfo"  width="300">([^</]*)', re.M)
        renum = re.compile('Number:</td>[^<td]*<td class="nextEpInfo" width="300">([^</]*)', re.M)
        reparachute = re.compile('However, our last information about it is: <br><br><b>([^<]*)', re.M)
    for sh in message.split(';'):
        sh = sh.strip()
        try:
            show = alias[sh].lower()
        except KeyError:
            show = sh
        show = show.replace(' ', '-').lower()
        if show == "":
            continue
        try:
            response = urllib2.urlopen("http://next-episode.net/%s" % show)
            if response.info().get("Content-Encoding") == "gzip":
                buf = StringIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                html = f.read()
            else:
                html = response.read()
            response.close()

            title = 'Pas de titre'
            if html == "Sorry. The url you are looking for is non existent.":
                res += "Le show %s n'existe pas\n"%(sh)

            date = redate.search(html).group(1)
            # Format : Thu Sep 23, 2010
            date = datetime.datetime.strptime(date, "%a %b %d, %Y")
            date = date.strftime("%d/%m/%Y")
        
            res += "Episode %s de %s : %sx%s : %s diffusé le %s\n" %  \
            (precornext, sh, reseason.search(html).group(1), renum.search(html).group(1).zfill(2), reep.search(html).group(1), date)
        except IOError:
            res += "Le show %s n'existe pas\n"%(sh)
        except AttributeError:
            # Ptet que c'est le show qui diffuse plus
            t = reparachute.search(html)
            if t:
                res += "Rien de prévu pour %s… Dernières infos : %s\n" %(sh, t.group(1))
            else:
                res += "Beenn euh ca existe mais la page de %s est pas correcte\n"%(sh)
    if res != "":
        return res[0:-1]
    else:
        return ""
