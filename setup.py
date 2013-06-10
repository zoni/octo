#!/usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
	with open('README.rst') as file:
		long_description = file.read()

	setup(name='octo',
	      version='0.2.3',
	      description='A plugin framework which allows you to write your application as a collection of (optionally interconnected) plugins.',
	      long_description=long_description,
	      author='Nick Groenen',
	      author_email='zoni@zoni.nl',
	      url='http://octo.zoni.nl',
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
