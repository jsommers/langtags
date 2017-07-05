from setuptools import setup

setup(
    name="langtags",
    version='2017.7.1',
    maintainer='Joel Sommers',
    maintainer_email='jsommers@colgate.edu',
    license="GPL v3",
    platforms=["any"],
    description="Checks whether a language tag conforms to BCP 47; provides some methods for looking up tags in the IANA registry",
    long_description="""
""",
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
