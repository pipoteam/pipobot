#! /usr/bin/python
#-*- coding: utf-8 -*-

liste_classes={}

def register(name, _class) :
    global liste_classes
    if name in liste_classes :
        liste_classes[name].append(_class)
    else :
        liste_classes[name] = [_class]
