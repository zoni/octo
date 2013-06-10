#!/usr/bin/env python

import octo
from setuptools import setup

if __name__ == "__main__":
	with open('README.rst') as file:
		long_description = file.read()

	setup(name='octo',
	      version=octo.__version__,
	      description=octo.__doc__,
	      long_description=long_description,
	      author=octo.__author__,
	      author_email=octo.__email__,
	      url=octo.__url__,
	      classifiers=[
	          "Environment :: Plugins",
	          "Topic :: Software Development :: Libraries :: Application Frameworks",
	          "Development Status :: 4 - Beta",
	          "Operating System :: POSIX :: Linux",
	          "Programming Language :: Python",
	          "Programming Language :: Python :: 2.7",
	          "Programming Language :: Python :: 3",
	          "Topic :: Software Development",
	          "Topic :: Utilities",
	      ],
	      license="License :: OSI Approved :: BSD License",
	      packages=['octo'],
	      scripts=['octo.py'],
	      install_requires=open('requirements.txt').readlines(),
	     )
