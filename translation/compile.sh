#!/bin/sh
#Compiling .po file to generate .mo translation file used by gettext
language=$1
if [ $# = 0 ];then
    language=fr_FR
fi
msgfmt -o $language.mo $language.po
mkdir -p ../pipobot/locale/$language/LC_MESSAGES
mv $language.mo ../pipobot/locale/$language/LC_MESSAGES/pipobot.mo
