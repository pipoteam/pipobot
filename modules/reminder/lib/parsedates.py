#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import time
import datetime
class ParseExcept(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def parsedate(day):
    day = day.lower()
    if "+" in day:
        try:
            nbday = int(day.partition("+")[2])
            if day.partition("+")[0] != "j":
                return None
            delta = datetime.timedelta(days=nbday)
            res = datetime.datetime.now() + delta
            return res.timetuple()
        except:
            return None
    else:
        formats = ["%d/%m/%y", "%d/%m/%Y"]
        for f in formats:
            try:
                datestruct = time.strptime(day, f)
                return datestruct
            except ValueError:
                pass
    return None

def parsehour(hour):
    hour = hour.lower()
    if "+" in hour:
        m_or_h, delta = hour.split("+")
        if m_or_h == "m":
            delta = datetime.timedelta(minutes = int(delta))
            res = datetime.datetime.now() + delta
            return res
        elif m_or_h == "h":
            delta = datetime.timedelta(hours = int(delta))
            res = datetime.datetime.now() + delta
            return res
        else:
            return None
    else:
        separators = ["h", ":"]
        for sep in separators:
            if sep in hour:
                hour, minute = hour.split(sep)
                if minute == "":
                    minute = 0
                hour = int(hour)
                minute = int(minute)
                now = datetime.datetime.now()
                return datetime.datetime(now.year, now.month, now.day, hour, minute)

def parseall(datehour):
    d = h = datehour
    for sep in [",", ";"]:
        if sep in datehour:
            d, h = datehour.split(sep)
    #on n'a spécifié que le jour ou que la date
    if d == datehour:
        d1 = parsedate(d)
        h1 = parsehour(h)
        #Si on a juste l'heure
        if d1 == None:
            return h1.timetuple()
        #Si on a juste le jour
        else:
            try:
                return d1.timetuple()
            except AttributeError:
                return d1
    #on a le jour et la date
    else:
        d1 = parsedate(d)
        h1 = parsehour(h)
        if d1 == None or h1 == None:
            raise ParseExcept("La date %s n'est pas valide !"%(datehour))
        d = datetime.datetime(d1.tm_year, d1.tm_mon, d1.tm_mday, h1.hour, h1.minute)
        return d.timetuple()



if __name__ == "__main__":
    dates = ["18/01/12", "J+1", "+1", "+10", "18/01/2012", "j+1"]
    hours = ["18h10", "18h", "1H", "H+1", "h+3"]
    dhs = ["18/01/12,18h10", "18h10", "J+1,18h02", "J+1,H+1", "M+30", "J+1", "h+3", "1h"]
    for dh in dhs: 
        print "-"*10
        print dh
        print parseall(dh)
        print time.mktime(parseall(dh))
        print time.strftime("%d/%m/%y,%Hh%M", time.localtime(time.mktime(parseall(dh))))
