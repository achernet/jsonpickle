#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- paulett.org)
# Copyright (C) 2009-2013 David Aguilar (davvid -at- gmail.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
try:
    from setuptools import setup, Extension, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Extension, find_packages
try:
    from Cython.Distutils import build_ext
except ImportError:
    from distutils.command.build_ext import build_ext


def get_version():
    from path import Path
    from importlib import import_module

    here = Path(__file__).abspath().dirname()
    version_file = here.joinpath('jsonpickle', 'version.py')
    version = eval(version_file.lines()[0].split('=')[-1].strip())
    return version


def get_requirements():
    from path import Path

    here = Path(__file__).abspath().dirname()
    reqs = here.joinpath('requirements.txt')
    return reqs.lines()


def main():
    setup(
        name='jsonpickle',
        version=get_version(),
        description='Python library for serializing any arbitrary object graph into JSON',
        setup_requires=[
            'Cython>=0.21.1',
            'path.py>=7.0'
        ],
        install_requires=get_requirements(),
        tests_require=[
            'ipython>=2.3.1',
            'unittest2>=0.8.0',
            'coverage>=3.7.1',
            'sphinx>=1.2.3',
            'nose>=1.3.4',
            'mock>=1.0.1',
        ],
        ext_modules=[
            Extension(name='jsonpickle.util',
                      sources=['jsonpickle/util.pyx'],
                      depends=['jsonpickle/util.pxd'],
                      extra_compile_args=['-O3', '-Wall', '-march=native'],
                      extra_link_args=['-O3']),
        ],
        long_description='jsonpickle converts complex Python objects to and from JSON.',
        author='David Aguilar',
        author_email='davvid -at- gmail.com',
        url='http://jsonpickle.github.io/',
        license='BSD',
        platforms=['POSIX', 'Windows'],
        keywords=['json pickle', 'json', 'pickle', 'marshal',
                  'serialization', 'JavaScript Object Notation'],
        classifiers=[
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: JavaScript',
        ],
        options={'clean': {'all': 1}},
        packages=find_packages(exclude=['ez_setup']),
        include_package_data=True,
        zip_safe=False,
        cmdclass={'build_ext': build_ext}
    )


if __name__ == '__main__':  # pragma: no cover
    main()
