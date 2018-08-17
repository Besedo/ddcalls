# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

setup(
    name='ddcalls',
    version='0.0.2',
    description='Simple configurable calls for DeepDetect in python',
    url='https://github.com/EBazarov/ddcalls',
    author='Evgeny BAZAROV',
    author_email='baz.evgenii@gmail.com',
    license='Apache v2.0',
    packages=find_packages(),
    keywords=['calls', 'binding', 'deepdetect'],
    install_requires=[
        'numpy',
        'requests',
        'tensorboard_logger'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Apache v2.0 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    entry_points={
        'console_scripts': [
            'ddcalls-train=ddcalls.train:main',
            'ddcalls-predict=ddcalls.predict:main',
        ]
    },
)
