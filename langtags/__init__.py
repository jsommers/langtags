"""
langtags module.

This module contains classes to help parse and represent IANA language
tags, attempting to follow BCP47 (https://tools.ietf.org/html/bcp47).
"""
import sys
import re
import os
import enum
from collections import OrderedDict, defaultdict
import datetime

__all__ = [
    'InvalidSubtagError',
    'MalformedTagError',
    'Tag',
    'Subtag',
    'tag_is_valid',
    'tag_is_well_formed',
]


# based on http://schneegans.de/lv/
_bcp47_regex = re.compile("""
^
(
  (
    (
      (
        (?P<language23>
          [a-z]{2,3}
        )
        (-
          (?P<extlang>
            [a-z]{3}
          )
        ){0,3}
      )
      |
      (?P<language4>
        [a-z]{4}
      )
      |
      (?P<language58>
        [a-z]{5,8}
      )
    )

    (-(?P<script>
      [a-z]{4}
    ))?

    (-(?P<region>
      [a-z]{2}
      |
      [0-9]{3}
    ))?

    (-
      (?P<variant>
        [a-z0-9]{5,8}
        |
        [0-9][a-z0-9]{3}
      )
    )*

    (-
      (?P<extensions>
        [a-wy-z0-9]
        (-
          [a-z0-9]{2,8}
        )+
      )
    )*

    (-
      (?P<privateusesubtags>x
        (-
          (
            [a-z0-9]{1,8}
          )
        )+
      )
    )?
  )
  |
  (?P<privateusetags>
    x(-
      (
        [a-z0-9]{1,8}
      )
    )+
  )
  |
  (?P<grandfathered>
    (?P<irregular>
      en-GB-oed |
      i-ami |
      i-bnn |
      i-default |
      i-enochian |
      i-hak |
      i-klingon |
      i-lux |
      i-mingo |
      i-navajo |
      i-pwn |
      i-tao |
      i-tay |
      i-tsu |
      sgn-BE-FR |
      sgn-BE-NL |
      sgn-CH-DE
    )
    |
    (?P<regular>
      art-lojban |
      cel-gaulish |
      no-bok |
      no-nyn |
      zh-guoyu |
      zh-hakka |
      zh-min |
      zh-min-nan |
      zh-xiang
    )
  )
)
$
""", re.VERBOSE | re.IGNORECASE)


def tag_is_well_formed(s):
    """Check whether a language tag is well-formed according to bcp47."""
    return _bcp47_regex.match(s) is not None


def tag_is_valid(s):
    """Check whether tag is well-formed and has valid contents."""
    try:
        Tag(s)
    except InvalidSubtagError:
        return False
    except MalformedTagError:
        return False
    else:
        return True


def _normalize(s):
    """Replace _ and / with - in an attempt to put tag in expected form."""
    return s.replace('_', '-').replace('/', '-')


class InvalidSubtagError(Exception):
    """
    InvalidSubtagError exception.

    Represents the fact that a tag includes invalid subtags (i.e.,
    subtags that are not found in the IANA language-subtag-registry).
    """
    pass


class MalformedTagError(Exception):
    """
    MalformedTagError exception.

    Represents the fact that a tag does not correctly follow the
    language tag syntax required by BCP 47.
    """
    pass


class SubtagRecordType(enum.IntEnum):
    """
    SubtagRecordType class.

    Represents the subtag record type, using the same terminology
    as the IANA language-subtag-registry.
    """
    Language = 1
    Extlang = 2
    Script = 3
    Region = 4
    Variant = 5
    Grandfathered = 6
    Redundant = 7
    Private = 8
    Extensions = 9


_regex_name_to_enum = OrderedDict([
    ('language23', SubtagRecordType.Language),
    ('language4', SubtagRecordType.Language),
    ('language58', SubtagRecordType.Language),
    ('extlang', SubtagRecordType.Extlang),
    ('script', SubtagRecordType.Script),
    ('region', SubtagRecordType.Region),
    ('variant', SubtagRecordType.Variant),
    ('grandfathered', SubtagRecordType.Grandfathered),
    ('extensions', SubtagRecordType.Extensions),
    ('privateusesubtags', SubtagRecordType.Private),
    ('privateusetags', SubtagRecordType.Private),
])


class _LanguageSubtagRegistry(object):
    """
    LanguageSubtagRegistry class.

    Internal class that encapsulates the IANA language-subtag-registry.
    Provides methods to load the registry and match
    a string tag against entries in the registry.
    Users will normally use the Tag/Subtag classes instead of
    directly accessing the registry through this class.
    """
    def __init__(self):
        self._recs = {}
        for e in SubtagRecordType:
            if e == SubtagRecordType.Private:
                self._recs[e] = defaultdict(str)
            else:
                self._recs[e] = {}

    def match(self, tag):
        """Return Subtag objects for each subtag in a full tag."""
        mobj = re.match(_bcp47_regex, tag)
        if mobj is None:
            raise MalformedTagError(tag)

        objs = []
        gdict = mobj.groupdict()
        for k, v in _regex_name_to_enum.items():
            matched_subtag = gdict.get(k, None)
            if matched_subtag is not None:
                if v is SubtagRecordType.Private:
                    r = Subtag({'Type': 'private',
                                'Tag': gdict[k]})
                else:
                    r = self._recs[v].get(matched_subtag.lower())
                    if r is None:
                        raise InvalidSubtagError(gdict[k])
                objs.append(r)
        return objs

    @staticmethod
    def load(infile="language-subtag-registry"):
        """Load the IANA registry; return new LanguageSubtagRegistry object."""
        def _extract_info(xlines):
            xdict = defaultdict(list)
            for line in xlines:
                if ': ' not in line:
                    break
                try:
                    idx = line.find(':')
                    if idx == -1:
                        raise ValueError("Failed on line {}".format(line))
                    key = line[:idx].strip()
                    val = line[(idx+1):].strip()
                except ValueError:
                    print("Failed on line {line}".format(line=line))
                    sys.exit(0)
                xdict[key].append(val)
            return {k: '\n'.join(v) for k, v in xdict.items()}

        def _load_group(inp):
            line = inp.readline()
            xlines = []
            while line and not line.startswith('%%'):
                # handle line continuation
                if line.startswith('  '):
                    xlines[-1] += ' ' + line.strip()
                else:
                    xlines.append(line.strip())
                line = inp.readline()
            return _extract_info(xlines)

        reg = _LanguageSubtagRegistry()
        recs = reg._recs

        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        with open(os.path.join(location, infile)) as inp:
            line = inp.readline()
            # first, eat first 2 lines to get to first record
            while not line.startswith('%%'):
                line = inp.readline()

            while True:
                xgroup = _load_group(inp)
                if not xgroup:
                    break
                recobj = Subtag(xgroup)
                # NB: put dict keys in lowercase
                recs[recobj.rectype][recobj.subtag.lower()] = recobj
        return reg


class Subtag(object):
    """
    Subtag class.

    Represents an individual subtag within a language tag.
    """
    def __init__(self, rec):
        self._type = getattr(
            SubtagRecordType.Language, rec.get('Type').capitalize())
        if 'Subtag' in rec:
            self._subtag = rec.get('Subtag')
            self._tag = ''
        if 'Tag' in rec:
            self._tag = rec.get('Tag')
            self._subtag = ''
        self._description = rec.get('Description', '')
        self._comments = rec.get('Comments', '')

        def _make_date(s):
            if not s:
                return None
            return datetime.datetime.strptime(s, "%Y-%m-%d").date()
        self._added = _make_date(rec.get('Added', ''))
        self._deprecated = _make_date(rec.get('Deprecated', ''))

        self._preferred_value = rec.get('Preferred-Value', '')
        self._suppress_script = rec.get('Suppress-Script', '')
        self._macrolanguage = rec.get('Macrolanguage', '')
        self._scope = rec.get('Scope', '')
        self._prefix = rec.get('Prefix', '')

    @property
    def rectype(self):
        """-> SubtagRecordType; get the subtag type"""
        return self._type

    @property
    def scope(self):
        """->str; get the subtag scope"""
        return self._scope

    @property
    def subtag(self):
        """->str; get the subtag"""
        return self._subtag if self._subtag else self._tag

    @property
    def tag(self):
        """->str; get the tag"""
        return self._tag if self._tag else self._subtag

    @property
    def macrolanguage(self):
        """-> str; get the macrolanguage, if any"""
        return self._macrolanguage

    @property
    def added(self):
        """->str; get the date added"""
        return self._added

    @property
    def comments(self):
        """-> str; get any comments about the subtag"""
        return self._comments

    @property
    def description(self):
        """->str; get any description of the subtag"""
        return self._description

    @property
    def preferred_value(self):
        """->str; get any preferred value for the subtag"""
        return self._preferred_value

    @property
    def prefix(self):
        """->bool; get any prefix for the subtag"""
        return self._prefix

    @property
    def suppress_script(self):
        """->str; get indication of whether script should be suppressed"""
        return self._suppress_script

    @property
    def is_deprecated(self):
        """->bool; check whether subtag is deprecated"""
        return self._deprecated is not None

    @property
    def deprecated_date(self):
        """->str; date of subtag deprecation, if any"""
        return self._deprecated

    def __str__(self):
        if self._type == SubtagRecordType.Region:
            return self._subtag.upper()
        elif self._type == SubtagRecordType.Script:
            return self._subtag.title()
        return self.subtag.lower()

    def __repr__(self):
        repdict = {
          'Type': self._type.name,
        }
        if self._subtag:
            repdict['Subtag'] = self._subtag
        else:
            repdict['Tag'] = self._tag

        def _maybe_include(attr):
            a = getattr(self, "_{}".format(attr).replace('-', '_'))
            if a:
                repdict[attr.title()] = str(a)

        _maybe_include('description')
        _maybe_include('added')
        _maybe_include('comments')
        _maybe_include('preferred-value')
        _maybe_include('suppress-script')
        _maybe_include('macrolanguage')
        _maybe_include('scope')
        _maybe_include('prefix')
        _maybe_include('deprecated')
        return "Subtag({})".format(repdict)


class Tag(object):
    """
    Tag class: a language tag.

    May be composed of multiple subtags (of type langtags.Subtag).
    Each Subtag, in keeping with BCP 47, narrows the range of language
    identified by the overall tag.

    Subtags can be accessed as would items in a list (indexing, len).

    It is also possible to access a subtag by record type, e.g.,
    tag.language, tag.script, tag.region. tag.variant, etc. (attributes
    are lower-cased versions of SubtagRecordType names).  If the
    attribute doesn't exist, None is returned.
    """
    def __init__(self, strtag='', normalize=False):
        if normalize:
            strtag = _normalize(strtag)
        subs = _registry.match(strtag)
        # we only get here if strtag is well-formed
        self._subtags = subs
        self._byrectype = {}
        for s in self._subtags:
            self._byrectype[s.rectype.name.lower()] = s

    def __getattr__(self, attr):
        if attr in self._byrectype:
            return self._byrectype[attr]

    def __getitem__(self, idx):
        if idx < 0:
            idx = len(self._subtags) + idx
        return self._subtags[idx]

    def __str__(self):
        return "-".join([str(s) for s in self._subtags])

    def __repr__(self):
        return "Tag('{}')".format(str(self))

    def __len__(self):
        return len(self._subtags)


# global object; the subtag registry
_registry = _LanguageSubtagRegistry.load()
