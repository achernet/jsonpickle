cd jsonpickle
cython --annotate --warning-extra --include-dir . --line-directives --force --embed-positions util.pyx
gcc -pthread -fno-strict-aliasing -g -O0 -fwrapv -Wall -fPIC -Wstrict-prototypes -I. -I/opt/zonar/python/python-2.7/include/python2.7 -march=native --coverage -c util.c -o util.o
gcc -pthread -shared util.o -L/opt/zonar/python/python-2.7/lib -lpython2.7 -g -O0 --coverage -o util.so
cd ..
python test.py
cd jsonpickle
mkdir -p /tmp/jsonpickle
lcov --capture --directory . --derive-func-data --rc branch-coverage=1 --output-file=jsonpickle.info
genhtml --function-coverage --branch-coverage --num-spaces=4 --highlight --output-directory=/tmp/jsonpickle --legend --sort jsonpickle.info
google-chrome /tmp/jsonpickle/index.html &
