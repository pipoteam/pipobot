#!/usr/bin/python
# -*- coding: UTF-8 -*-

def humanize_time(secs):
    secs = int(secs.partition(".")[0])
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    secs = str(secs).zfill(2)
    mins = str(mins).zfill(2)
    hours = str(hours).zfill(2)
    return '%sh%sm%ss' % (hours,mins, secs)

def format(song):
    """Formatte joliment un fichier"""
    artiste = song["artist"] if "artist" in song.keys() else "<unkown>"
    titre   = song["title"] if "title" in song.keys() else "<unkown>"
    
    if artiste == "<unkown>" and titre == "<unkown>":
        return "%s. %s" % (song["pos"], song["file"])
    else:
        return "%s. %s - %s" % (song["pos"], artiste, titre)
