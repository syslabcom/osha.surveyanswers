# -*- coding: utf-8 -*-
"""
This module contains the osha.policy package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.9.8dev'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('osha', 'surveyanswers', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

setup(name='osha.surveyanswers',
      version=version,
      description="Transform a file like object into a flash view",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        ],
      keywords='osha survey',
      author='Patrick Gerken',
      author_email='gerken@syslab.com',
      url='http://products.syslab.com/products/',
      license='GPL + EUPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'xlwt',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'mock',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
