#!/usr/bin/env python

from setuptools import setup
import glob
import os
import sys

requirements=['nose>=1.3.0', 'requests', 'stitches>=0.12']

# Workaround for https://github.com/paramiko/paramiko/issues/1123
python_version=sys.version_info[0] + sys.version_info[1] / 10.0
if python_version <= 2.6:
    requirements.append('paramiko==2.3.1')

datafiles = []
for topdir in ['rhui3_tests']:
    for dirname, dirnames, filenames in os.walk(topdir):
        datafiles.append(('share/rhui3_tests_lib/' + dirname, map(lambda x: dirname + "/" + x, filenames)))

setup(name='rhui3_tests_lib',
    version='1.0',
    description='RHUI3 Testing Library',
    author='Martin Minar',
    author_email='mminar@redhat.com',
    url='https://github.com/RedHatQE/rhui3-automation',
    license="GPLv3+",
    packages=[
        'rhui3_tests_lib'
        ],
    data_files=datafiles,
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Operating System :: POSIX',
            'Intended Audience :: Developers',
            'Development Status :: 5 - Production/Stable'
    ],
    scripts=glob.glob('scripts/*.py') + glob.glob('scripts/*.sh')
)

