#!/usr/bin/env python
#-*- coding: utf8 -*-
import urllib
import simplejson
from pipobot.lib.modules import SyncModule, defaultcmd
import pipobot.lib.utils

class CmdGoogle(SyncModule):
    def __init__(self, bot):
        desc = u"!google mot-clé : recherche le mot clé dans google"
        SyncModule.__init__(self,
                            bot, 
                            desc = desc,
                            command = "google")
    
    @defaultcmd
    def answer(self, sender, message):
        if message == '':
            return self.desc
        else:
            query = urllib.urlencode({'q': message})
            url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % (query)
            search_results = urllib.urlopen(url)
            json = simplejson.loads(search_results.read())
            results = json['responseData']['results']

            ans = ''
            ans_xhtml = ''
            for i in results:
                ans += '\n' + i['url'] + ' --- ' + i['title']
                ans_xhtml += '<br/>\n<a href="' + i['url'] + '" >' + i['title'] + '</a>'
                ans_xhtml = ans_xhtml.replace("b>", "strong>")
            rep = {}
            rep["text"] = pipobot.lib.utils.xhtml2text(ans)
            rep["xhtml"] = ans_xhtml
            return rep
