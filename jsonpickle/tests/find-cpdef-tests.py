#!/usr/bin/env python
""" Find defs, cpdefs in pyx files, print calls in tests """
from __future__ import division, print_function

DESCRIP = "Find def and cpdef functions / methods, look for calls in tests"
EPILOG = \
"""Search for all ".pyx" files at given file root.

Find all functions and method definitions in the pyx files by looking for
"def " or "cpdef " followed by an identifier and open parentheses.

Search for all tests by looking for files at same file root with "test" in the
file name.

Analyze test files syntax tree for calls to found "def" and "cpdef" functions.

Print list of "def" and "cpdef" functions, with matching test file lines, or
warning that the function / method is not tested.
"""

import os
import re
from os.path import join as pjoin
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import ast


def call_finder(tree):
    """ Return function / method names of all calls in a syntax `tree`

    Parameters
    ----------
    tree : ast tree
        ast syntax tree resulting from ``ast.parse``

    Returns
    -------
    called_names : list
        List with entries ``(name, line_no)`` where ``name`` is the function or
        method name called, ``line_no`` is the 1-based line number in the
        source file of the call.
    """
    called_names = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            raise ValueError('Confused by node.func type ' +
                             str(type(node.func)))
        called_names.append((name, node.lineno))
    return sorted(called_names, key = lambda x : x[1])


def test_call_finder():
    # Run with nose tests
    from nose.tools import assert_equal
    def p(source):
        return call_finder(ast.parse(source))
    assert_equal(p('func()'), [('func', 1)])
    assert_equal(p('my.func(arg)'), [('func', 1)])
    assert_equal(p('my.func(arg); some.other.funky()'),
                 [('func', 1), ('funky', 1)])


def find_pyxes(root):
    """ Find "*.pyx" files starting at path `root`

    Omit directories called ``build``
    """
    pyxes = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != 'build']
        for fbase in filenames:
            if not fbase.endswith('.pyx'):
                continue
            pyxes.append(pjoin(dirpath, fbase))
    return pyxes


def find_tests(root):
    """ Find test files starting at path `root`

    Accept any file with string "test" in filename.

    Omit directories called ``build``
    """
    test_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != 'build']
        for fbase in filenames:
            if not 'test' in fbase:
                continue
            test_files.append(pjoin(dirpath, fbase))
    return test_files


DEF_RE = re.compile('\s*(def|cpdef)\s+([a-zA-Z0-9]+\s+)*([a-zA-z0-9_]*)\(')


def find_defs(pyx_fname):
    """ Find "def" and "cpdef" function / method definitions in `pyx_fname`

    Parameters
    ----------
    pyx_fname : str
        ".pyx" file path

    Returns
    -------
    pyx_defs : dict
        key, value pairs of ``(identifier, info_dict)`` where ``identifier`` is
        the function or method name, and ``info_dict`` is a dict giving:

        * def_type : "def" or "cpdef"
        * line : code line containing definition
        * line_no : 0-based line number of ``line`` in `pyx_fname` file.
    """
    pyx_defs = {}
    with open(pyx_fname, 'rt') as fobj:
        lines = fobj.readlines()
    for no, line in enumerate(lines):
        def_match = DEF_RE.match(line)
        if def_match is None:
            continue
        def_type, ret_type, def_name = def_match.groups()
        assert def_name not in pyx_defs # probably will be so
        pyx_defs[def_name] = dict(
            type = def_type,
            line = line.strip(),
            line_no = no)
    return pyx_defs


def fuse_pyx_defs(pyx_defs_dicts, pyx_fnames):
    """ Fuse sequence of `pyx_defs` dictionaries into one

    Parameters
    ----------
    pyx_defs_dicts : sequence
        Sequence of ``pyx_defs``, where a `pyx_defs` is a dictionary with key,
        value pairs of ``(identifier, info_dict)`` where ``identifier`` is the
        function or method name, and ``info_dict`` is a dict giving:

        * def_type : "def" or "cpdef"
        * line : code line containing definition
        * line_no : 0-based line number of ``line`` in `pyx_fname` file.
    pyx_fnames : sequence
        sequence of pyx file filenames, matching 

    Returns
    -------
    pyx_defs_fused : dict
        `pyx_defs_dicts` dictionaries merged, with filename included in values
    """
    fused_defs = {}
    for pyx_fname, pyx_defs in zip(pyx_fnames, pyx_defs_dicts):
        for name in pyx_defs:
            assert not name in fused_defs # not usually the case
            fused_defs[name] = pyx_defs[name]
            fused_defs[name]['pyxfile'] = pyx_fname
    return fused_defs


def find_defs_used(test_fname, pyx_defs):
    """ Return all `pyx_defs` used in test `test_fname`
    """
    defs_used = {}
    with open(test_fname, 'rt') as fobj:
        source = fobj.read()
    lines = [line.strip() for line in source.splitlines()]
    tree = ast.parse(source, test_fname)
    for name, line_no in call_finder(tree):
        if name not in pyx_defs:
            continue
        if name not in defs_used:
            defs_used[name] = []
        defs_used[name].append((line_no, lines[line_no - 1]))
    return defs_used


def fuse_defs_used(tests, tests_defs):
    """ Rearrange test defs by name """
    by_name = {}
    for test, test_def in zip(tests, tests_defs):
        for name in test_def:
            if name not in by_name:
                by_name[name] = []
            for tested_def in test_def[name]:
                line_no, line = tested_def
                by_name[name].append(
                    dict(test = test,
                         line_no = line_no,
                         line = line))
    return by_name


def print_fused_tests_defs(fused_tests_defs, fused_pyx_defs):
    """ Nice output of ".pyx" functions / methods with test file lines
    """
    fname_names = {}
    for name, info in fused_pyx_defs.items():
        fname = info['pyxfile']
        if fname not in fname_names:
            fname_names[fname] = []
        fname_names[fname].append(name)
    for fname in sorted(fname_names):
        print(fname, ':')
        lines_names = [(fused_pyx_defs[n]['line_no'], n)
                       for n in fname_names[fname]]
        for line_no, name in sorted(lines_names):
            name_line = '{0}, {1}'.format(name, line_no + 1) # 1-based
            if name not in fused_tests_defs:
                print(' ', name_line, 'might be untested')
                continue
            print(' ', name_line)
            for tester in fused_tests_defs[name]:
                print('    {}, {}, {}'.format(
                    tester['test'],
                    tester['line_no'],
                    tester['line']))


def main():
    parser = ArgumentParser(description=DESCRIP,
                            epilog=EPILOG,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('code_path',  type=str,
                        help='Code path for pyx files / tests')
    # parse the command line
    args = parser.parse_args()
    pyxes = find_pyxes(args.code_path)
    tests = find_tests(args.code_path)
    pyx_defs = [find_defs(pyx_fname) for pyx_fname in pyxes]
    fused_defs = fuse_pyx_defs(pyx_defs, pyxes)
    tests_defs = [find_defs_used(test, fused_defs) for test in tests]
    fused_tests_defs = fuse_defs_used(tests, tests_defs)
    print_fused_tests_defs(fused_tests_defs, fused_defs)


if __name__ == '__main__':
    main()