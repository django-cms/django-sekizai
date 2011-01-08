#!/bin/bash
cd tests

args=("$@")
num_args=${#args[@]}
index=0

reuse_env=true
disable_coverage=true
suite="sekizai"
python="/bin/python"

while [ "$index" -lt "$num_args" ]
do
    case "${args[$index]}" in
        "--failfast")
            failfast="--failfast"
            ;;

        "--rebuild-env")
            reuse_env=false
            ;;

        "--with-coverage")
            disable_coverage=false
            ;;

        "--help")
            echo ""
            echo "usage:"
            echo "    runtests.sh"
            echo "    or runtests.sh [flags]"
            echo ""
            echo "flags:"
            echo "    --failfast - abort at first failing test"
            echo "    --with-coverage - enables coverage"
            echo "    --rebuild-env - run buildout before the tests"
            echo "    --python /path/to/python - set python to use"
            exit 1
            ;;

        *)
            suite="sekizai.${args[$index]}"
    esac
    let "index = $index + 1"
done

if [ $reuse_env == false ]; then
    echo "setting up test environment (this might take a while)..."
    python bootstrap.py
    if [ $? != 0 ]; then
        echo "bootstrap.py failed"
        exit 1
    fi
    ./bin/buildout
    if [ $? != 0 ]; then
        echo "bin/buildout failed"
        exit 1
    fi
else
    echo "reusing current buildout environment"
fi

if [ $disable_coverage == false ]; then
    ./bin/coverage run --rcfile=.coveragerc testapp/manage.py test $suite $failfast
    retcode=$?

    echo "Post test actions..."
    ./bin/coverage xml
    ./bin/coverage html
else
    ./bin/django test $suite $failfast
    retcode=$?
fi
cd ..
echo "done"
exit $retcode