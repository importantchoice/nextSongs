#!/usr/bin/env python3

from setuptools import setup

setup(
    name='nextSongs',
    version='0.1',
    packages=['nextSongs'],
    entry_points={
            'console_scripts': [
                'nextSongs = nextSongs.ui:main',
            ],
    },
)
