#!/usr/bin/python
# -*- coding: UTF-8 -*-
from mercurial import ui, hg, commands
from mercurial.cmdutil import show_changeset
import mercurial.commands
import time

def log(repodir, rev = -1):
    u = ui.ui()
    repo = hg.repository(u, repodir)
    if rev == -1:
        rev = len(repo) - 1
    elif rev > len(repo) or rev < 0:
        return "%s n'est pas une révision valide" % rev
    stamp = repo[rev].date()[0]
    date = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(stamp))
    user = repo[rev].user()
    desc = repo[rev].description()
    res = "#%s : %s (le %s par %s)" % (rev, desc, date, user)
    return res

if __name__ == "__main__":
    print log("/srv/hg/repos/botjabber")
