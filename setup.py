from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cloudomate',

    version='1.0.0',

    description='Automate buying VPS instances with Bitcoin',
    long_description=long_description,

    url='https://github.com/Jaapp-/Cloudomate',

    author='PlebNet',
    author_email='plebnet@heijligers.me',

    license='LGPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Installation/Setup',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],

    keywords='vps bitcoin',

    packages=find_packages(exclude=['docs', 'test']),

    install_requires=['appdirs', 'lxml', 'MechanicalSoup', 'bs4', 'mock', 'forex-python', 'parameterized'],

    extras_require={
        'dev': [],
        'test': ['mock', 'parameterized'],
    },

    package_data={
        'cloudomate': [],
    },

    entry_points={
        'console_scripts': [
            'cloudomate=cloudomate.cmdline:execute',
        ],
    },
)
