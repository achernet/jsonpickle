#!/usr/bin/env python
import sh
from path import Path
import jsonpickle
import sys


def find_tests():
    mod_file = Path(jsonpickle.__file__).dirname()
    parent_dir = mod_file
    while parent_dir.basename() == 'jsonpickle':
        parent_dir = mod_file.dirname()

        if parent_dir.basename() == 'jsonpickle':
            mod_file = parent_dir
            continue


def main():
    mod_file = Path(jsonpickle.__file__).dirname()
    test_files = [str(path) for path in mod_file.walkfiles('test_*.py')]
    nose_args = ['-v', '-v', '--with-coverage', '--cover-branches',
                 '--cover-inclusive', '--cover-erase', '--cover-html',
                 '--cover-package=jsonpickle']
    nose_args.extend(test_files)
    cmd = sh.Command('nosetests')
    cmd = cmd.bake(nose_args, _iter=True, _tty_out=False, _err_to_out=True)
    for line in cmd():
        sys.stdout.write(line)


if __name__ == '__main__':  # pragma: no cover
    main()
