#!/bin/bash
cd tests
echo "setting up test environment (this might take a while)..."
python bootstrap.py >/dev/null 2>&1
./bin/buildout >/dev/null 2>&1
./bin/coverage run ./testapp/manage.py test testapp
retcode=$?
./bin/coverage xml --omit=parts,/usr/,eggs
cd ..
exit $retcode
