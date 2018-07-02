from cloudomate.globals import __version__
from codecs import open
from os import path
import sys


from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

if sys.version_info.major == 2:
    package_data = {
        b'cloudomate': [],
    }
else:
    package_data = {
        'cloudomate': [],
    }

setup(
    name='cloudomate',

    version=__version__,

    description='Automate buying VPS instances with Bitcoin',
    long_description=long_description,

    url='https://github.com/tribler/cloudomate',

    author='PlebNet',
    author_email='authentic8989@gmail.com',

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

    install_requires=[
        'appdirs',
        'lxml',
        'MechanicalSoup',
        'CurrencyConverter',
        'bs4',
        'forex-python',
        'parameterized',
        'fake-useragent',
        'CaseInsensitiveDict',
        'ConfigParser',
        'future',
        'requests[security]'
    ],

    extras_require={
        'dev': [],
        'test': ['mock', 'parameterized'],
    },

    package_data=package_data,

    entry_points={
        'console_scripts': [
            'cloudomate=cloudomate.cmdline:execute',
        ],
    },
)
