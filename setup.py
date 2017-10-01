import sys
from setuptools import setup


setup(
    name="langtags",
    version='2017.9.1',
    maintainer='Joel Sommers',
    maintainer_email='jsommers@colgate.edu',
    url="https://github.com/jsommers/langtags",
    license="GPL v3",
    platforms=["any"],
    description="Provides simple format and content validation for language tags based on BCP 47 and the IANA language tag registry.",
    packages=['langtags'],
    include_package_data=True,
    package_data={'': ['language-subtag-registry']},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
