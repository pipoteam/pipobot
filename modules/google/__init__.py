#!/usr/bin/env python
#-*- coding: utf8 -*-
import urllib
import simplejson
from lib.modules import SyncModule, answercmd

class CmdGoogle(SyncModule):
    def __init__(self, bot):
        desc = u"!google mot-clé : recherche le mot clé dans google"
        SyncModule.__init__(self,
                            bot, 
                            desc = desc,
                            command = "google")
    
    @answercmd
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
                ans = ans.replace("b>", "strong>")
                ans_xhtml = ans_xhtml.replace("b>", "strong>")
            rep = {}
            rep["text"] = ans
            rep["text"] = ans_xhtml
            return rep
