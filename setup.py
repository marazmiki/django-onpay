#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
import os
import sys

py_version = sys.version_info
version = __import__('onpay').get_version()
readme = os.path.join(os.path.dirname(__file__), 'README.rst')

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Framework :: Django'
]

install_requires = ['django',
                    'python-dateutil',
                    'six']
tests_require = ['django',
                 'six']


if isinstance(py_version, tuple):
    if py_version < (2, 7):
        install_requires.append('importlib')


setup(
    name='django-onpay',
    author='Mikhail Porokhovnichenko <marazmiki@gmail.com>',
    version=version,
    author_email='marazmiki@gmail.com',
    url='http://pypi.python.org/pypi/django-onpay',
    download_url='http://bitbucket.org/marazmiki/django-ulogin/get/tip.zip',
    description='onpay',
    long_description=open(readme).read(),
    license='MIT license',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=install_requires,
    packages=find_packages(exclude=['test_project', 'test_project.*']),
    test_suite='tests.main',
    tests_require=tests_require,
    include_package_data=True,
    zip_safe=False)