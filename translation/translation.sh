#!/bin/sh
#Reading source code to extract text to translate and generate .po file
language=$1
if [ $# = 0 ];then
    language="fr_FR"
fi
#Version of the project
tip=`hg tip |grep changeset |cut -d":" -f 2 | sed "s/ //g"`
#Date of the project
date=`date +"%d-%m-%Y"`

if [ -f $language.po ]; then
    cp $language.po messages.po
else
    sed "s/\[LANGUAGE\]/$language/g" headers.po | sed "s/\[VERSION\]/$tip/g" |sed "s/\[DATE\]/$date/g" > messages.po
fi

for file in `find ".." -name "*.py"`
do
    xgettext -j --language=python --omit-header $file
done
mv messages.po $language.po
