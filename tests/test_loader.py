import unittest

from pipobot.lib.loader import import_fct


class ImporterTest(unittest.TestCase):
    def test_importer(self):
        from pipobot.lib.utils import rot13
        fct = import_fct("pipobot.lib.utils.rot13")
        self.assertEqual(fct("pipo", "pipo"), rot13("pipo", "pipo"))

        fct = import_fct("foo.bar.useless", path=["tests/var"])
        self.assertEqual(fct("pipo", "pipo"), 42)
