#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='utils',
    author='foo-manroot',
    version='1.0',
    author_email='foo@oi.m8',
    description='Custom transforms with some utilities to ease the work flow',
    license='GPLv3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    package_data={
        '': ['*.gif', '*.png', '*.conf', '*.mtz', '*.machine']  # list of resources
    },
    install_requires=[
        'canari>=3.0'
        , 'geopy >= 1.12.0'
        , 'phonenumbers >= 8.9.2'
        , 'pycountry >= 18.2.23'

    ],
    dependency_links=[
        # custom links for the install_requires
    ]
)
