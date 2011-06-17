#!/usr/bin/env python
#-*- coding: utf8 -*-
import urllib
import simplejson

class CmdGoogle:
    def __init__(self, bot):
        self.bot = bot
        self.command = u"google"
        self.desc = u"!google mot-clé : recherche le mot clé dans google"
	self.pm_allowed = True

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
            return (ans, ans_xhtml)

if __name__ == '__main__':
    #Placer ici les tests unitaires
    o = CmdGoogle(None)
    print o.answer('xouillet', 'bok ounet')
    print o.answer('xouillet', '')
else:
    from .. import register
    register(__name__, CmdGoogle)


