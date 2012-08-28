#!/bin/sh
#
# This script generates a .pot file for the projet. If an argument or more is given, it
# insteads generate the .po file for the language(s) given as argument (from an
# existing .pot file).
#
cd ..
version=$(python2 -c "from pipobot import __version__; print (__version__)")
cd -

if [ $# = 0 ]; then
    gerenate_pot=1
elif [ ! -f po/pipobot.pot ]; then
    generate_pot=1
fi

if [ generate_pot ]; then
    # We have to generate the .pot file on which the .po files will be based.
    xgettext    --language=Python \
                --keyword=_ \
                --output=po/pipobot.pot \
                --from-code=UTF-8 \
                --package-name=pipobot \
                --package-version=$version \
                --msgid-bugs-address="pipoteam@xouillet.info" \
                --copyright-holder="Pipoteam" \
                `find ../pipobot -name "*.py"`
fi

# Generate all the .po files that the user requested
while (( "$#" )); do
    locale=$1

    msginit --input=po/pipobot.pot --locale=$locale --output=po/$locale.po
    shift
done
