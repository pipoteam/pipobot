#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""Module used to parse dates in several formats : 
   Global format : date,hour
   Format for date : dd/mm/yy, dd/mm/YYYY, J+n = 'in [n] days'
   Format for hour : HH:MM, HHhMM , H+n = 'in [n] hours', M+n = 'in [n] minutes'
"""
import time
import datetime


class ParseExcept(Exception):
    """ Custom exception if a date/hour is not valid """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return self.msg

def parsedate(day):
    """ Parsing a date with formats : dd/mm/yy, dd/mm/YYYY, J+n = 'in [n] days' """
    day = day.lower()
    if "+" in day:
        try:
            #Case J+n
            nbday = int(day.partition("+")[2])
            if day.partition("+")[0] != "j":
                return None
            #We take 'now' date and we add [n] days
            delta = datetime.timedelta(days=nbday)
            res = datetime.datetime.now() + delta
            return res.timetuple()
        except:
            return None
    else:
        #If we specify a complete date
        formats = ["%d/%m/%y", "%d/%m/%Y"]
        #We search a matching format
        for f in formats:
            try:
                datestruct = time.strptime(day, f)
                return datestruct
            except ValueError:
                pass
    return None

def parsehour(hour):
    """ Parsing a date with formats : HH:MM, HHhMM , H+n = 'in [n] hours """
    hour = hour.lower()
    #Cases of H+n or M+n
    if "+" in hour:
        m_or_h, delta = hour.split("+")
        #M+n
        if m_or_h == "m":
            delta = datetime.timedelta(minutes = int(delta))
            res = datetime.datetime.now() + delta
            return res
        #H+n
        elif m_or_h == "h":
            delta = datetime.timedelta(hours = int(delta))
            res = datetime.datetime.now() + delta
            return res
        #Error
        else:
            return None
    #Cases HHhMM or HH:MM
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
    """Method to parse a date, hour"""
    d = h = datehour
    #We try to separate date and hour
    for sep in [",", ";"]:
        if sep in datehour:
            d, h = datehour.split(sep)
    #Only date or only hour is present
    if d == datehour:
        d1 = parsedate(d)
        h1 = parsehour(h)
        #We have just the date
        if d1 is None:
            return h1.timetuple()
        #We have just the hour
        else:
            try:
                return d1.timetuple()
            except AttributeError:
                return d1
    #We have date and hour
    else:
        parsed_date = parsedate(d)
        parsed_hour  = parsehour(h)
        #date or hour are invalid
        if parsed_date is None or parsed_hour is None:
            raise ParseExcept(_("The date %s is not valid !")% datehour)
        #We have date combining parsed date and hour
        final_date = datetime.datetime(parsed_date.tm_year, parsed_date.tm_mon, parsed_date.tm_mday, 
                                       parsed_hour.hour, parsed_hour.minute)
        return final_date.timetuple()

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
