from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='osha.surveyanswers',
      version=version,
      description="Transform a file like object into a flash view",
      long_description=open("README.txt").read() + "\n" + 
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Patrick Gerken',
      author_email='gerken@syslab.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      paster_plugins=["ZopeSkel"],
      )
