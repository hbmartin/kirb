#!/usr/bin/env python
from setuptools import setup, find_packages
NAME='kirb'
setup(name=NAME,
      version='1.4',
      license='BSD',
      url='https://github.com/hbmartin/kirb',
      description='Continuous Integration & ReBuild',
      author='Harold Martin',
      author_email='harold.martin@openx.com',
      packages=find_packages(),
      long_description=open('README.txt').read(),
      package_data = { '': ['*.txt', '*.rst'] },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Documentation',
          'Topic :: Utilities',
      ],
      platforms='any',
      namespace_packages=[NAME],
      install_requires = ['docutils>=0.3','watchdog>=0.6']
     )

