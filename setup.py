import sys
from setuptools import setup

if sys.version_info.major < 3:
    print("langtags is a Python 3-only module.  Sorry!")
    sys.exit()


setup(
    name="langtags",
    version='2017.8.1',
    maintainer='Joel Sommers',
    maintainer_email='jsommers@colgate.edu',
    license="GPL v3",
    platforms=["any"],
    description="Provides simple format and content validation for language tags based on BCP 47 and the IANA language tag registry.",
    packages=['langtags'],
    include_package_data=True,
    package_data={'langtags': ['language-subtag-registry']},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
