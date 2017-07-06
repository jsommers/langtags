langtags
========

The purpose of ``langtags`` is to provide some simple mechanisms by which language tags can be parsed and *validated*.  By *validation*, I mean that their *structure* can be compared with the expected structure specified in IETF BCP 47 (https://tools.ietf.org/html/bcp47) and that their *contents* can be compared with entries in the IANA language subtag registry (https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry).  

``langtags`` is Python 3-only.

A basic use-case is as follows::

    >>> import langtags
    >>>
    >>> # check a tag for validity
    >>> tag = langtags.Tag("en-Latn-US")
    >>>
    >>> # string conversion results in a canonical form tag
    >>> print(tag)
    en-Latn-US
    >>>
    >>> # without string conversion, you can see that there's a Tag object
    >>> tag
    <langtags.Tag object at 0x1009d7860>
    >>>
    >>> # subtags can be accessed by component name
    >>> tag.language
    <langtags.SubtagRegistryRecord object at 0x1009f7828>
    >>> tag.language.subtag
    'en'
    >>> tag.script.subtag
    'Latn'
    >>> tag.region.subtag
    'US'
    >>>
    >>> # if there's no subtag component of a given name, None is returned
    >>> tag.private
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
