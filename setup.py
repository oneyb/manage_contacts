#!/usr/bin/env python3

DESCRIPTION = "Easy personal contact file management"
LONG_DESCRIPTION = """
   manage_contacts is dedicated to collecting contacts in vcf-format
   for contact management.
   Some of the features that manage_contacts offers are:

   - read in all vcf-files recursively in a directory
   - output as org-contacts formatted org-file 
   - output as all vcf-files as a single sorted, uniqued vcf-file
"""

DISTNAME = 'manage_contacts'
MAINTAINER = 'Brian J. Oney'
MAINTAINER_EMAIL = 'brian.j.oney@gmail.com'
URL = 'https://github.com/oneyb/manage_contacts'
LICENSE = 'GPLv2'
DOWNLOAD_URL = 'https://github.com/oneyb/manage_contacts'
VERSION = '0.1'

try:
    from setuptools import setup
    _has_setuptools = True
except ImportError:
    from distutils.core import setup


def check_dependencies():
    install_requires = []
    try:
        import vobject
    except ImportError:
        install_requires.append('vobject')

    return install_requires


if __name__ == "__main__":

    install_requires = check_dependencies()

    setup(name=DISTNAME,
          author=MAINTAINER,
          author_email=MAINTAINER_EMAIL,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          install_requires=install_requires,
          entry_points={
              'console_scripts': [
                  'manage_contacts=manage_contacts.manage_contacts:main',
              ],
          },
          packages=['manage_contacts'],
          classifiers=[
              'Intended Audience :: Entrepreneurial/Inventory',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              'License :: OSI Approved :: GPLv2 License',
              'Topic :: Multimedia :: Graphics',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS'],
)
