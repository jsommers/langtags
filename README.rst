langtags
========

The purpose of ``langtags`` is to provide some simple mechanisms by which language tags can be parsed and *validated*.  In this context, *validation* means that the *structure* of a language tag can be compared with the expected structure specified in IETF BCP 47 (https://tools.ietf.org/html/bcp47) and that a tag's *contents* (i.e., subtags) can be found in the IANA language subtag registry (https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry).

The langtags module is meant to be simple and efficient.  Its primary purpose is tag validation, at present.  It does *not* do any "canonicalization" of language tags (e.g., remove script subtags that are indicated via a Suppress-Script attribute, or replace subtags with any preferred values, etc.)  Use cases for langtags will generally revolve around (1) validating a language tag for correct structure and contents, and (2) looking up IANA language subtag registry information regarding subtags within a tag.

If you need to look up language tags by language name (e.g., obtain 'en' record from 'English'), the langcodes module is a good choice.  It is rather difficult, however, to use the langcodes module to determine whether a given language tag contains invalid subtags (i.e., subtags that don't exist in the IANA language subtag registry).  This module aims to be simpler, with strict BCP 47 compliance checking and validation.

``langtags`` is Python 3-only.

A basic use-case is as follows::

    >>> import langtags
    >>>
    >>> # check a tag for validity
    >>> tag = langtags.Tag("en-Latn-US")
    >>>
    >>> # implicit or explicit string conversion results in a canonical form
    >>> tag
    Tag('en-Latn-US')
    >>> print(tag)
    en-Latn-US
    >>>
    >>> # subtags can be accessed by component name
    >>> tag.language
    Subtag({'Type': 'Language', 'Subtag': 'en', 'Description': 'English', 'Added': '2005-10-16', 'Suppress-Script': 'Latn'})
    >>> tag.language.subtag
    'en'
    >>> tag.script.subtag
    'Latn'
    >>> tag.region.subtag
    'US'
    >>>
    >>> # if there's no subtag component of a given name, None is returned
    >>> tag.private is None
    True
    >>> tag.extlang is None
    True
    >>>
    >>> # if a tag is invalid, an exception is raised
    >>> tag = langtags.Tag("cy-GB-Latn")
    Traceback (most recent call last):
        ...
        raise MalformedTagError(strtag)
    langtags.MalformedTagError: cy-GB-Latn
    >>>
    >>> # case doesn't matter when tags are created, but
    >>> tag = langtags.Tag("cy-gb")
    >>>
    >>> # the library will still string-convert into canonical form
    >>> print(tag)
    cy-GB
    >>>
    >>> # subtags can also be accessed via indexing
    >>> tag[0]
    Subtag({'Type': 'Language', 'Subtag': 'cy', 'Description': 'Welsh', 'Added': '2005-10-16', 'Suppress-Script': 'Latn'})
    >>> tag[-1]
    Subtag({'Type': 'Region', 'Subtag': 'GB', 'Description': 'United Kingdom', 'Added': '2005-10-16', 'Comments': 'as of 2006-03-29 GB no longer includes the Channel Islands and Isle of Man; see GG, JE, IM'})
    >>>
    >>> # len() works on a tag
    >>> len(tag)
    2
    >>>
    >>> # any of the IANA record fields can be accessed, in lower-case
    >>> # *except* that the Type field is named rectype
    >>> tag[1].rectype
    <SubtagRecordType.Region: 4>
    >>> tag[1].subtag
    'GB'
    >>> tag[1].description
    'United Kingdom'
    >>> tag[1].added
    datetime.date(2005, 10, 16)
    >>> tag[1].comments
    'as of 2006-03-29 GB no longer includes the Channel Islands and Isle of Man; see GG, JE, IM'
    >>>
    >>> # very simple malformed tags can be normalized before parsing
    >>> tag = langtags.Tag('gd_GB')
    Traceback (most recent call last):
        ...
    langtags.MalformedTagError: gd_GB
    >>> tag = langtags.Tag('gd_GB', normalize=True)
    >>> print(tag)
    gd-GB


The code and documentation are both works in progress.


License
-------

Copyright 2017 Joel Sommers.  All rights reserved.

The langtags software is distributed under terms of the GNU General Public License, version 3.  See below for the standard GNU GPL v3 copying text.

::

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
