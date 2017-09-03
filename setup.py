#!/usr/bin/env python3

from setuptools import setup

setup(
    name='nextSongs',
    version='0.1.0',
    packages=['nextSongs'],
    include_package_data=True,
    entry_points={
            'console_scripts': [
                'nextSongs = nextSongs.ui:main',
            ],
    },
)
