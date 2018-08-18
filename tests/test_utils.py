import unittest

import pipobot.lib.utils as utils

from pipobot.lib.module_test import create_test_bot


class TestUtils(unittest.TestCase):
    def test_xhtml2text(self):
        ret = utils.xhtml2text("<b>bold</b>")
        self.assertEqual(ret, "*bold*")
        ret = utils.xhtml2text("<strong>bold</strong>")
        self.assertEqual(ret, "*bold*")
        ret = utils.xhtml2text("<u>under</u>")
        self.assertEqual(ret, "_under_")
        ret = utils.xhtml2text("<a href='http://some_url'>link name</a>")
        self.assertEqual(ret, "link name")
        ret = utils.xhtml2text("<b>&#33;</b>")
        self.assertEqual(ret, "*!*")
        ret = utils.xhtml2text("<u>&#x26;</u>")
        self.assertEqual(ret, "_&_")
        ret = utils.xhtml2text("<u>&#xpipo;</u>")
        self.assertEqual(ret, "_&#xpipo;_")
        ret = utils.xhtml2text("<u>&amp;</u>")
        self.assertEqual(ret, "_&_")
        ret = utils.xhtml2text("<u>&pipopouet;</u>")
        self.assertEqual(ret, "_&pipopouet;_")

    def test_mute(self):
        bot = create_test_bot([])
        utils.mute("bob", "parce que", bot)
        data = bot.output.get()
        self.assertEqual(data["type"], "set")
        self.assertEqual(data["query"], "http://jabber.org/protocol/muc#admin")
        self.assertEqual(data["to"], bot.chatname)

        item = data.xml.getchildren()[0].getchildren()[0]
        self.assertEqual(item.get("role"), "visitor")
        self.assertEqual(item.get("nick"), "bob")
        self.assertEqual(item.getchildren()[0].text, "parce que")

    def test_unmute(self):
        bot = create_test_bot([])
        utils.unmute("bob", "parce que", bot)
        data = bot.output.get()
        self.assertEqual(data["type"], "set")
        self.assertEqual(data["query"], "http://jabber.org/protocol/muc#admin")
        self.assertEqual(data["to"], bot.chatname)

        item = data.xml.getchildren()[0].getchildren()[0]
        self.assertEqual(item.get("role"), "participant")
        self.assertEqual(item.get("nick"), "bob")
        self.assertEqual(item.getchildren()[0].text, "parce que")

    def test_kick(self):
        bot = create_test_bot([])

        utils.kick("bob", "parce que", bot)
        data = bot.output.get()
        self.assertEqual(data["type"], "set")
        self.assertEqual(data["query"], "http://jabber.org/protocol/muc#admin")
        self.assertEqual(data["to"], bot.chatname)

        item = data.xml.getchildren()[0].getchildren()[0]
        self.assertEqual(item.get("role"), "none")
        self.assertEqual(item.get("nick"), "bob")
        self.assertEqual(item.getchildren()[0].text, "parce que")

    def test_check_url(self):
        url = "http://httpbin.org/"
        ret = utils.check_url(url)
        self.assertEqual(ret, ['[Lien] Titre : httpbin.org'])

        url = "http://httpbin.org/gzip"
        ret = utils.check_url(url)[0]
        self.assertRegexpMatches(ret, '\[Lien\] Type: application/json, Taille : (\d+) octets')

        url = "http://httpbin.org/digest-auth/auth/user/passwd"
        ret = utils.check_url(url)
        self.assertEqual(ret, ["Je ne peux pas m'authentifier sur %s :'(" % url])

        ret = utils.check_url("http://httpbin.org/html")
        self.assertEqual(ret, ["[Lien] Titre : Pas de titre"])

        url = "http://httpbin.org/qsdfqsdfqsdf"
        ret = utils.check_url(url)
        self.assertEqual(ret, ["%s n'existe pas !" % url])

        url = ("hp://httpbin.org/qsdfqsdfqsdf")
        ret = utils.check_url(url)
        self.assertEqual(ret, ["L'URL %s n'est pas valide !" % url])

        url = ("http://httpbin.org/status/403")
        ret = utils.check_url(url)
        self.assertEqual(ret, ["Il est interdit d'accéder à %s !" % url])

        url = ("http://httpbin.org/status/418")
        ret = utils.check_url(url)
        self.assertEqual(ret, ["Erreur 418 sur %s" % url])

        url = "http://httpbin.org"
        ret = utils.check_url(url, True)
        self.assertEqual(ret, ['%s : [Lien] Titre : httpbin.org' % url])

    def test_color(self):
        ret = utils.color("pipo", "cyan")
        self.assertEqual(ret, "\033[0;36mpipo\033[0m")
